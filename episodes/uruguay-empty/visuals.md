# Uruguay: visual inventory (2026-11-26)

Licences: PD / CC0 / CC BY only (pipeline/commons.py checks). Search: tools/find_media.py and a scratch category lister
(scratch catlist.py); every file in build_script passed the sharpness check (episode_check, detail >= 0.65, or 600-1400 px
for the Real-ESRGAN upscale). Contact sheets of the final picks: scratch photos0-2.jpg.

## Sources that carried the episode
- **Centro de Fotografía de Montevideo (CdF)** glass negatives on Commons ("... - 0xxxxFMHGE.tif", "FMHE", "FMHB"), public
  domain: La Tablada cattle market 1920, Swift plant on the Cerro 1918/1958, Arroyo Pantanoso 1926, Liebig Fray Bentos 1919,
  port and old town aerials 1919-1936, Rambla 1919-1948, Central Station 1900/1917, Isla de Flores quarantine 1921, Salto 1919.
  They carry black frames and a grey-scale strip: the script uses `#crop=0.07,0.07,0.06,0.16` (new in commons.fetch).
- **"El Uruguay a través de un siglo" (1910) / "El Libro del Centenario" (1925)** page scans: estancias 1910, cattle wagon
  of the Central Railway, Liebig saladero 1907, saladero work 1907, cattle drive at Molles 1907. Captions cut with `#crop`.
- **US Embassy Montevideo (PD)**: Fiesta de la Patria Gaucha, Tacuarembó, 14 March 2026 (riders, gauchos). Only crowd and
  rider frames; none centred on the ambassador.
- **GRU-MVD flight 2026-06-21 (CC BY 4.0)**: modern aerials of Montevideo (only frames that clearly show the city).
- Modern countryside (CC0, 2017 series): Tacuarembó, Río Tacuarembó, Ruta 30 near Tranqueras, Río Negro department,
  windmills in northern Uruguay; Ovinos; eucalyptus row "Countryside in Montevideo".
- Rio Grande do Sul: São Leopoldo 1924 and 1971, Caxias 1883 and 1932, Jaguari colony plan 1898 (CC0), Serra Gaúcha,
  Gramado vineyards, Rivera / Santana do Livramento border.
- Buenos Aires: Immigrants' Hotel (LOC LCCN 91739070; Google Arts & Culture c. 1912).
- Paintings (PD): Blanes (Artigas en la Ciudadela; Rivera portrait), Carbajal (Artigas in Paraguay 1873), Laroche 1906,
  Escena campestre; Saravia photos 1903-04; Batlle 1904 drawing; Bordaberry inauguration 1972 (CdF).

## Rejected
Soft or small: Blanes "Juramento de los 33" (detail 0.52), Rugendas Rivera, Liebig poster 1890, BA immigrants 1904/1931,
Hotel de Inmigrantes Montevideo 0522FMHB, Sierra de los Caracoles wind farm, Planta UPM 2 (CC0), Rincón del Bonete 2026,
Batlle 2, siege plan of 1789 harbour, Caxias 1971 aerial. Wrong content: "Caxias do Sul, Brazil (Unsplash)" is a dog,
"RenatoSoares ... Salton" is champagne glasses, "La Embajadora Kelly Keiderling visita Rivera" is the UTEC building,
"Donación de equipos para tratamiento de agua" shows two officials at a press call.

## Satellite (Sentinel-2), scratch uysat.py, window 2024-12-15/2025-02-28 (southern summer)
Clear on every view: Montevideo city, old town/port, Cerro and the bay, Colonia, Fray Bentos (Anglo), UPM Fray Bentos,
UPM Paso de los Toros, Paso Severino (also 2023-07-14 in the drought), Agraciada fields, Masoller grass, Durazno,
Tacuarembó plantations, Rivera plantations, Rivera/Livramento, Caxias do Sul, the Campanha near Dom Pedrito, Punta del Este.
Winter 2022 at Paso Severino: no clear scene (the drought comparison uses the two PD false-colour images on Commons).

## Gaps
No free photo of Salsipuedes, Masoller battle, the 1973 coup itself, the 2002 bank run or the 2023 water crisis in the
streets; maps, cards and present-day views carry those sentences.
