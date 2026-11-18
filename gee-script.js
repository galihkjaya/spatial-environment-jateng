var jatengCoastROI = ee.Geometry.Polygon([
  [[108.80, -6.95],
   [111.70, -6.60],
   [111.70, -6.40],
   [108.80, -6.75]]
]);

Map.centerObject(jatengCoastROI, 9);
Map.setOptions('HYBRID');

function maskS2clouds(image) {
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  return image.updateMask(mask).divide(10000);
}

function getDrySeasonComposite(year) {
  var startDate = ee.Date.fromYMD(year, 6, 1);
  var endDate = ee.Date.fromYMD(year, 9, 30);
  
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(jatengCoastROI)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 25))
    .map(maskS2clouds)
    .median()
    .clip(jatengCoastROI);
}

var s2_2020 = getDrySeasonComposite(2020);
var s2_2023 = getDrySeasonComposite(2023);
var s2_2026 = getDrySeasonComposite(2026);

function calcMNDWI(image, name) {
  return image.normalizedDifference(['B3', 'B11']).rename(name);
}

var mndwi_2020 = calcMNDWI(s2_2020, 'mndwi_2020');
var mndwi_2023 = calcMNDWI(s2_2023, 'mndwi_2023');
var mndwi_2026 = calcMNDWI(s2_2026, 'mndwi_2026');

var water_2020 = mndwi_2020.gt(0).rename('water_2020');
var water_2023 = mndwi_2023.gt(0).rename('water_2023');
var water_2026 = mndwi_2026.gt(0).rename('water_2026');

var abrasi_fase1 = water_2020.eq(0).and(water_2023.eq(1)).rename('abrasi_1');
var akresi_fase1 = water_2020.eq(1).and(water_2023.eq(0)).rename('akresi_1');

var abrasi_fase2 = water_2023.eq(0).and(water_2026.eq(1)).rename('abrasi_2');
var akresi_fase2 = water_2023.eq(1).and(water_2026.eq(0)).rename('akresi_2');

var abrasi_total = water_2020.eq(0).and(water_2026.eq(1)).rename('abrasi_total');
var akresi_total = water_2020.eq(1).and(water_2026.eq(0)).rename('akresi_total');

Map.addLayer(s2_2026, {bands: ['B4', 'B3', 'B2'], min: 0.0, max: 0.28}, 'Citra Satelit RGB Asli (2026)', false);
Map.addLayer(water_2026.selfMask(), {palette: ['#1f77b4']}, 'Kondisi Garis Air Laut (2026)', false);

Map.addLayer(akresi_total.selfMask(), {palette: ['#00FF00']}, 'Akresi / Sedimentasi (2020-2026)', true);
Map.addLayer(abrasi_total.selfMask(), {palette: ['#FF0000']}, 'HOTSPOT ABRASI TOTAL (2020-2026)', true);

var pixelAreaHa = ee.Image.pixelArea().divide(10000);

function hitungLuasHa(imageLayer, bandName) {
  var stats = imageLayer.multiply(pixelAreaHa).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: jatengCoastROI,
    scale: 20,
    maxPixels: 1e10
  });
  return stats.get(bandName);
}

var luasAbrasiFase1 = hitungLuasHa(abrasi_fase1, 'abrasi_1');
var luasAkresiFase1 = hitungLuasHa(akresi_fase1, 'akresi_1');

var luasAbrasiFase2 = hitungLuasHa(abrasi_fase2, 'abrasi_2');
var luasAkresiFase2 = hitungLuasHa(akresi_fase2, 'akresi_2');

var luasAbrasiTotal = hitungLuasHa(abrasi_total, 'abrasi_total');
var luasAkresiTotal = hitungLuasHa(akresi_total, 'akresi_total');

Export.image.toDrive({
  image: abrasi_total.byte(),
  description: 'Raster_Abrasi_Pesisir_Jateng_2020_2026',
  folder: 'GEE_Projek_Statling_Jateng',
  fileNamePrefix: 'raster_abrasi_jateng_2020_2026',
  region: jatengCoastROI,
  scale: 20,
  maxPixels: 1e10
});

Export.image.toDrive({
  image: s2_2026.select(['B4', 'B3', 'B2']).visualize({min: 0.0, max: 0.28}),
  description: 'Peta_Satelit_RGB_Pesisir_Jateng_2026',
  folder: 'GEE_Projek_Statling_Jateng',
  fileNamePrefix: 'citra_rgb_pantura_jateng_2026',
  region: jatengCoastROI,
  scale: 20,
  maxPixels: 1e10
});

var summaryTable = ee.FeatureCollection([
  ee.Feature(null, {
    'Periode': 'Fase 1 (2020-2023)',
    'Fenomena_Iklim': 'Triple-Dip La Nina & Rob Mei 2022',
    'Luas_Abrasi_Ha': luasAbrasiFase1,
    'Luas_Akresi_Ha': luasAkresiFase1
  }),
  ee.Feature(null, {
    'Periode': 'Fase 2 (2023-2026)',
    'Fenomena_Iklim': 'Godzilla Super El Nino & Sediment Deficit',
    'Luas_Abrasi_Ha': luasAbrasiFase2,
    'Luas_Akresi_Ha': luasAkresiFase2
  }),
  ee.Feature(null, {
    'Periode': 'Total (2020-2026)',
    'Fenomena_Iklim': 'Net Cumulative Loss (2020-2026)',
    'Luas_Abrasi_Ha': luasAbrasiTotal,
    'Luas_Akresi_Ha': luasAkresiTotal
  })
]);

Export.table.toDrive({
  collection: summaryTable,
  description: 'Tabel_Statistik_Abrasi_Jateng_CSV',
  folder: 'GEE_Projek_Statling_Jateng',
  fileNamePrefix: 'tabel_statistik_abrasi_jateng_2020_2026',
  fileFormat: 'CSV'
});