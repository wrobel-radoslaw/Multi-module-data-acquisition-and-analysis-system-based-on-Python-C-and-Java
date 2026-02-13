package org.example;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import okhttp3.*;
import org.knowm.xchart.*;
import org.knowm.xchart.style.*;
import org.knowm.xchart.style.markers.SeriesMarkers;
import org.knowm.xchart.style.lines.SeriesLines;

import javax.swing.*;
import java.io.*;
import java.time.*;
import java.util.*;

public class App {

    private static final Map<String, String> TICKERS = Map.of(
        "CDR", "CD Projekt SA",
        "PKO", "Powszechna Kasa Oszczędności Bank Polski SA",
        "PKN", "Orlen SA",
        "KGH", "KGHM Polska Miedź SA",
        "CCC", "CCC SA"
    );

    private record StockData(LocalDate date, double price) {
        static StockData parseLine(String[] line) {
            // Columns: [Date, Open, High, Low, Close, Volume]
            return new StockData(LocalDate.parse(line[0]), Double.parseDouble(line[4]));
        }
    }
    private static final OkHttpClient client = new OkHttpClient();

    public static void main(String[] args) {
        try (Scanner sc = new Scanner(System.in)) {
            while (true) {
                System.out.println("================================");
                System.out.println("Polish GPW Stock Market Analysis");
                System.out.println("================================");
                System.out.println("1. Enter ticker (e.g. CDR) to download data and display charts");
                System.out.println("2. Type LIST to display sample GPW companies");
                System.out.println("3. Type Q to exit:");
                System.out.print("Your choice: ");

                String input = sc.nextLine().trim().toUpperCase();

                if (input.equals("Q") || input.equals("EXIT") || input.equals("QUIT")) { 
                    System.out.println("Closing..."); 
                    // Important: This forces the JVM to close even if windows are running in the background
                    System.exit(0); 
                }
                
                if (input.equals("LIST")) { 
                    displayTickerList();
                    continue;
                }
                
                if (input.isEmpty()) continue;

                System.out.println("Downloading data for: " + input + "...");

                try {
                    List<StockData> hist = parseCsv(downloadCsv(input));
                    
                    if (hist.isEmpty()) { System.out.println("ERROR: No data for this ticker. Try LIST."); continue; }
                    
                    StockData last = hist.get(hist.size() - 1);
                    System.out.printf("Downloaded %d quotes. Last closing price (%s): %.2f PLN%n", 
                                      hist.size(), last.date(), last.price());

                    drawCharts(input, hist);
                } catch (Exception e) {
                    System.out.println("ERROR: Failed to process data. Make sure the ticker is correct.");
                } finally {
                    System.out.println("\nPress Enter to continue...");
                    sc.nextLine();
                }
            }
        }
    }
    
    private static void displayTickerList() {
        System.out.println("\n--- GPW Ticker List ---");
        System.out.println("A ticker is an abbreviation used to identify a company on the Warsaw Stock Exchange (GPW).");
        System.out.println("Below are some examples you can use:");
        
        System.out.printf("%-10s %s%n", "TICKER", "COMPANY NAME");
        System.out.println("----------------------------------------");
        
        for (Map.Entry<String, String> entry : TICKERS.entrySet()) {
            System.out.printf("%-10s %s%n", entry.getKey(), entry.getValue());
        }
    }

    private static String downloadCsv(String ticker) throws IOException {
        Request req = new Request.Builder()
            .url("https://stooq.pl/q/d/l/?s=" + ticker.toLowerCase() + "&i=d")
            .header("User-Agent", "Mozilla/5.0 (W)") 
            .build();

        try (Response res = client.newCall(req).execute()) {
            if (!res.isSuccessful()) throw new IOException("HTTP Code: " + res.code());
            String body = res.body().string();
            return body.contains("No data") ? null : body; 
        }
    }

    private static List<StockData> parseCsv(String csv) throws IOException, CsvValidationException {
        List<StockData> data = new ArrayList<>();
        if (csv == null) return data;
        
        try (CSVReader r = new CSVReader(new StringReader(csv))) {
            r.readNext();
            String[] line;
            while ((line = r.readNext()) != null) 
                if (line.length >= 5 && line[4] != null && !line[4].isEmpty() && !line[4].equals("NaN")) 
                    try { data.add(StockData.parseLine(line)); } catch (Exception ignored) {}
        }
        data.sort(Comparator.comparing(StockData::date));
        return data;
    }

    private static List<Double> calculateSMA(List<StockData> hist, int period) {
        List<Double> sma = new ArrayList<>();
        for (int i = 0; i < hist.size(); i++) {
            if (i < period - 1) { sma.add(Double.NaN); } 
            else {
                double sum = 0;
                for (int j = 0; j < period; j++) sum += hist.get(i - j).price();
                sma.add(sum / period);
            }
        }
        return sma;
    }

    private static List<Double> calculateMomentum(List<StockData> hist, int period) {
        List<Double> mom = new ArrayList<>();
        for (int i = 0; i < hist.size(); i++) {
            if (i < period) mom.add(Double.NaN); 
            else mom.add((hist.get(i).price() / hist.get(i - period).price()) * 100);
        }
        return mom;
    }

    private static List<Double> calculateRSI(List<StockData> hist, int period) {
        List<Double> rsiList = new ArrayList<>();
        double[] diffs = new double[hist.size()];
        for (int i = 1; i < hist.size(); i++) diffs[i] = hist.get(i).price() - hist.get(i - 1).price();

        double avgGain = 0;
        double avgLoss = 0;

        for (int i = 1; i <= period; i++) {
            if (diffs[i] > 0) avgGain += diffs[i];
            else avgLoss -= diffs[i]; 
        }
        avgGain /= period;
        avgLoss /= period;

        for (int i = 0; i < hist.size(); i++) {
            if (i < period) {
                rsiList.add(Double.NaN);
                if (i == period - 1) { 
                    double rs = avgLoss == 0 ? (avgGain == 0 ? 0 : 2) : avgGain/avgLoss; 
                    rsiList.set(i, 100 - (100 / (1 + rs)));
                }
            } else {
                double gain = diffs[i] > 0 ? diffs[i] : 0;
                double loss = diffs[i] < 0 ? -diffs[i] : 0;

                avgGain = (avgGain * (period - 1) + gain) / period;
                avgLoss = (avgLoss * (period - 1) + loss) / period;

                double rs = avgLoss == 0 ? (avgGain == 0 ? 0 : 2) : avgGain / avgLoss; 
                rsiList.add(100 - (100 / (1 + rs)));
            }
        }
        return rsiList;
    }

    // --- HELPER METHOD FOR DISPLAYING CHARTS IN "DO NOT KILL APPLICATION" MODE ---
    private static void displayChartWindow(XYChart chart) {
        SwingWrapper<XYChart> wrapper = new SwingWrapper<>(chart);
        JFrame frame = wrapper.displayChart();
        // This is the key line - DISPOSE instead of EXIT
        frame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
    }

    private static void drawCharts(String ticker, List<StockData> hist) {
        List<Date> xData = hist.stream()
                .map(d -> Date.from(d.date().atStartOfDay(ZoneId.systemDefault()).toInstant())).toList();
        List<Double> yPrice = hist.stream().map(StockData::price).toList();
        List<Double> ySMA50 = calculateSMA(hist, 50);
        List<Double> yMomentum14 = calculateMomentum(hist, 14);
        List<Double> yRSI14 = calculateRSI(hist, 14);

        // 1. PRICE CHART WITH SMA50 (Trend)
        XYChart priceChart = new XYChartBuilder().width(800).height(400)
        .title("1. Price and SMA 50: " + ticker).xAxisTitle("Date").yAxisTitle("Price (PLN)").theme(Styler.ChartTheme.Matlab).build();
        priceChart.getStyler().setLegendPosition(Styler.LegendPosition.InsideNW);
        priceChart.getStyler().setDatePattern("yyyy-MM-dd");
        priceChart.getStyler().setXAxisLabelRotation(45);
        priceChart.addSeries("Closing Price", xData, yPrice).setMarker(SeriesMarkers.NONE);
        priceChart.addSeries("SMA 50 days", xData, ySMA50).setMarker(SeriesMarkers.NONE);
        
        // 2. MOMENTUM OSCILLATOR CHART
        XYChart momentumChart = new XYChartBuilder().width(800).height(300)
            .title("2. Momentum 14 days (rate of change)").xAxisTitle("Date").yAxisTitle("Value (%)").theme(Styler.ChartTheme.Matlab).build();
        momentumChart.getStyler().setDatePattern("yyyy-MM-dd");
        momentumChart.getStyler().setXAxisLabelRotation(45);
        momentumChart.addSeries("Momentum (14)", xData, yMomentum14).setMarker(SeriesMarkers.NONE);

        // 3. RSI OSCILLATOR CHART
        XYChart rsiChart = new XYChartBuilder().width(800).height(300)
            .title("3. Relative Strength Index (RSI) 14 days").xAxisTitle("Date").yAxisTitle("Value (0-100)").theme(Styler.ChartTheme.Matlab).build();
        rsiChart.getStyler().setDatePattern("yyyy-MM-dd");
        rsiChart.getStyler().setXAxisLabelRotation(45);
        rsiChart.getStyler().setYAxisMax(100.0);
        rsiChart.getStyler().setYAxisMin(0.0);

        // Overbought line (70) - BLUE
        rsiChart.addSeries("Overbought (70)", xData, Collections.nCopies(xData.size(), 70.0))
            .setMarker(SeriesMarkers.NONE).setLineStyle(SeriesLines.SOLID).setLineColor(java.awt.Color.BLUE);
        // Oversold line (30) - GREEN
        rsiChart.addSeries("Oversold (30)", xData, Collections.nCopies(xData.size(), 30.0))
            .setMarker(SeriesMarkers.NONE).setLineStyle(SeriesLines.SOLID).setLineColor(java.awt.Color.GREEN);

        rsiChart.addSeries("RSI (14)", xData, yRSI14).setMarker(SeriesMarkers.NONE);

        // Displaying in separate windows with safe closing
        displayChartWindow(priceChart);
        displayChartWindow(momentumChart);
        displayChartWindow(rsiChart);
    }
}