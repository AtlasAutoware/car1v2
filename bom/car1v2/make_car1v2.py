"""Car 1 v2 carts and budget. Every total is computed here, not typed.

    python3 bom/car1v2/make_car1v2.py   ->  cart_*.csv, shelf.csv, credits.csv, BUDGET.md (same folder)

Price basis ("basis" column):
  cart     read in the DigiKey cart on 2026-11-09 (Web ID 379079317): price, stock and DigiKey's tariff estimate
  page     read on the seller's product page on 2026-11-09
  quote    an earlier quote, not re-read on 2026-11-09 (the date is in the note)
  est      an estimate; nobody has read a price for this exact item
Nothing here has been ordered.
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = '2026-11-09'

# ----------------------------------------------------------------------------- money in the bank
# Truthifi's free plan was at 5 of 5 credits on 2026-11-09 (resets 05:00 UTC Nov 10), so these are the
# fallback figures from the brief: the posted balance read earlier that day and four items still to post.
BANK_POSTED = 1895.60
BANK_PENDING = [('Mobile check deposit (Nov 9)', +250.00), ('Micro Center debit (Nov 9)', -199.11),
                ('PayPal to FS.COM (Nov 6)', -83.08), ('PayPal, bank part of the Adafruit payment (Nov 9)', -31.49)]
# What the three debits were, from the books audit of 2026-11-09: FS.COM is storage for a training computer; the Adafruit
# payment (55.50 in all) was filed under car parts on an assumption; the Micro Center purpose is not recorded. All three
# were spent before this design and are outside the 1,500.
CAP = 1500.00
SALES_TAX = 0.06      # Fairfax County, VA combined rate. ASSUMED, not looked up on 2026-11-09.
PCB_DUTY = 0.35       # JLCPCB's published US DDP rate for bare PCBs since 2026-03-17; PCBWay's own figure shows at checkout.

# ----------------------------------------------------------------------------- DigiKey cart as read
# (digikey_pn, mfr_pn, what, qty, unit, tariff_ext, availability, refs, action)
# action: keep | delete (wrong or backordered line still sitting in the cart) | phase2 (not part of stage 1)
DK = [
 ('36-5000-ND', '5000', 'Keystone test point, red', 10, 0.263, 0.40, 'in stock', 'TP101 TP102 TP301 TP401-403 TP701 TP1002 + 2', 'keep'),
 ('455-B4B-XH-A-ND', 'B4B-XH-A', 'JST XH header 4 pos', 2, 0.17, 0.10, 'in stock', 'J201 + 1', 'keep'),
 ('PC817X2NSZ9F-ND', 'PC817X2NSZ9F', 'optocoupler DIP-4', 6, 0.33, 0.99, 'in stock', 'U201 U202 U801 U802 + 2', 'keep'),
 ('448-IRFB7430PBF-ND', 'IRFB7430PBF', 'main switch FET 40 V TO-220', 4, 3.69, 5.54, 'in stock', 'Q301-Q303 + 1', 'keep'),
 ('576-1234-ND', 'MIC5014YN', 'high-side gate driver DIP-8', 2, 3.54, 0.00, 'in stock', 'U301 + 1', 'keep'),
 ('490-6544-2-ND', 'GRM32ER71H106KA12L', '10 uF 50 V X7R 1210, reel packaging', 7, 0.00, 0.00, 'BACKORDER', 'C301 C402 C403 C501 C702', 'delete'),
 ('296-1606-5-ND', 'SN74HCT08N', 'quad AND DIP-14', 2, 0.93, 0.00, 'in stock', 'U302 + 1', 'keep'),
 ('IRF9Z34NPBF-ND', 'IRF9Z34NPBF', 'P-FET 55 V TO-220', 3, 2.13, 0.00, 'in stock', 'Q304 Q405 + 1', 'keep'),
 ('2N3904FS-ND', '2N3904BU', 'NPN TO-92', 10, 0.179, 0.45, 'in stock', 'Q305 Q401 Q403 Q406 Q502 Q503 + 4', 'keep'),
 ('MF-R050-ND', 'MF-R050', 'polyfuse 0.5 A', 2, 0.47, 0.26, 'in stock', 'F301 + 1', 'keep'),
 ('10W-5-ND', 'SQP500JB-10R', '10 ohm 5 W cement', 2, 0.71, 0.50, 'in stock', 'R313 + 1', 'keep'),
 ('BC2301-ND', 'NTCLE100E3103JB0', '10k NTC', 2, 0.61, 0.12, 'in stock', 'TH301 + 1', 'keep'),
 ('160-1139-ND', 'LTL-4221N', 'LED red 3 mm', 4, 0.19, 0.05, 'backorder, due 2026-11-16', 'D302 D702 + 2', 'keep'),
 ('945-2201-ND', 'R-78E5.0-1.0', '5 V 1 A switching regulator', 1, 4.51, 1.13, 'in stock', 'U401', 'keep'),
 ('160-1142-ND', 'LTL-4231N', 'LED green 3 mm', 4, 0.19, 0.06, 'in stock', 'D403 D701 + 2', 'keep'),
 ('732-5316-ND', '61300311121', 'pin header 1x3', 4, 0.13, 0.06, 'in stock', 'J403 J406 J904 + 1', 'keep'),
 ('P14398-ND', 'EEU-FR1C102', '1000 uF 16 V', 2, 1.08, 0.16, 'BACKORDER (past due)', 'C404', 'delete'),
 ('36-3568-ND', '3568', 'mini blade fuse holder', 2, 1.31, 0.00, 'in stock', 'F401 F501', 'keep'),
 ('IRF4905PBF-ND', 'IRF4905PBF', 'P-FET 55 V 74 A TO-220', 3, 3.26, 3.67, 'in stock', 'Q402 Q501 + 1', 'keep'),
 ('P124227-ND', 'EEU-FR1V221', '220 uF 35 V', 2, 0.71, 0.11, 'BACKORDER to 2027-01-29', 'C405', 'delete'),
 ('MF-R075-ND', 'MF-R075', 'polyfuse 0.75 A', 3, 0.47, 0.41, 'in stock', 'F402 F403 + 1', 'keep'),
 ('277-1721-ND', '1984617', 'Phoenix terminal block 2 pos', 1, 0.59, 0.25, 'in stock', 'J409', 'keep'),
 ('732-2731-ND', '614004134726', 'USB-A receptacle', 1, 3.68, 1.10, 'in stock', 'J601', 'keep'),
 ('732-5317-ND', '61300411121', 'pin header 1x4', 3, 0.18, 0.08, 'in stock', 'J602 J603 + 1', 'keep'),
 ('MCP2221A-I/P-ND', 'MCP2221A-I/P', 'USB to UART DIP-14', 1, 3.20, 0.00, 'in stock', 'U601', 'keep'),
 ('MCP1700-3302E/TO-ND', 'MCP1700-3302E/TO', '3.3 V LDO TO-92', 2, 0.50, 0.01, 'in stock', 'U602 + 1', 'keep'),
 ('732-5401-ND', '61204021621', 'box header 2x20', 1, 1.15, 0.16, 'in stock', 'J801', 'keep'),
 ('732-5323-ND', '61301211121', 'pin header 1x12', 2, 0.54, 0.15, 'in stock', 'J802 + 1', 'keep'),
 ('CKN9092-ND', 'PTS645SL50-2 LFS', 'tactile switch 6 mm', 2, 0.28, 0.24, 'in stock', 'SW801 + 1', 'keep'),
 ('455-1709-ND', 'B7B-PH-K-S', 'JST PH header 7 pos', 2, 0.33, 0.07, 'in stock', 'J903 + 1', 'keep'),
 ('455-1704-ND', 'B2B-PH-K-S', 'JST PH header 2 pos', 2, 0.12, 0.02, 'in stock', 'J1001 + 1', 'keep'),
 ('455-1719-ND', 'S2B-PH-K-S', 'JST PH header 2 pos, side entry', 2, 0.12, 0.00, 'in stock', 'J1002 + 1', 'keep'),
 ('WM4330-ND', '0470531000', 'fan header 4 pos', 1, 0.56, 0.00, 'in stock', 'J1003', 'keep'),
 ('2N7000-G-ND', '2N7000-G', 'N-FET TO-92', 2, 0.50, 0.05, 'in stock', 'Q1001 + 1', 'keep'),
 ('A120347-ND', '1-2199298-2', 'DIP-8 socket', 2, 0.27, 0.16, 'in stock', 'U301 socket + 1', 'keep'),
 ('A120348-ND', '1-2199298-3', 'DIP-14 socket', 3, 0.28, 0.25, 'in stock', 'U302 U601 sockets + 1', 'keep'),
 ('S7018-ND', 'PPTC201LFBN-RC', 'socket strip 1x20', 2, 1.14, 0.00, 'in stock', 'Pico sockets', 'keep'),
 ('S7006-ND', 'PPTC081LFBN-RC', 'socket strip 1x8', 2, 0.58, 0.00, 'in stock', 'hub module sockets', 'keep'),
 ('S7002-ND', 'PPTC041LFBN-RC', 'socket strip 1x4', 1, 0.42, 0.00, 'in stock', 'hub module socket', 'keep'),
 ('2648-SC0917-ND', 'SC0917', 'Raspberry Pi Pico H (headers fitted)', 2, 5.00, 0.34, 'in stock', 'MOD701 + 1 spare', 'keep'),
 ('839-10-01779-ND', '10-01779', 'Tensility 5.5 x 2.5 mm right-angle DC lead', 1, 4.51, 3.32, 'in stock', 'dev-kit power lead', 'keep'),
 ('311-4.70KFRCT-ND', 'RC1206FR-074K7L', '4.7k 1206', 10, 0.053, 0.04, 'in stock', '7 used', 'keep'),
 ('311-470FRCT-ND', 'RC1206FR-07470RL', '470 1206', 10, 0.053, 0.04, 'in stock', '5 used', 'keep'),
 ('311-10.0FRCT-ND', 'RC1206FR-0710RL', '10 ohm 1206', 10, 0.086, 0.08, 'in stock', '3 used', 'keep'),
 ('311-2.20MFRCT-ND', 'RC1206FR-072M2L', '2.2M 1206', 10, 0.056, 0.04, 'in stock', '1 used', 'keep'),
 ('311-100KFRCT-ND', 'RC1206FR-07100KL', '100k 1206', 25, 0.0404, 0.08, 'in stock', '17 used', 'keep'),
 ('311-10.0KFRCT-ND', 'RC1206FR-0710KL', '10k 1206', 30, 0.0404, 0.09, 'in stock', '21 used', 'keep'),
 ('311-33.0KFRCT-ND', 'RC1206FR-0733KL', '33k 1206', 10, 0.053, 0.04, 'in stock', '1 used', 'keep'),
 ('311-22.0KFRCT-ND', 'RC1206FR-0722KL', '22k 1206', 10, 0.053, 0.04, 'in stock', '1 used', 'keep'),
 ('311-2.20KFRCT-ND', 'RC1206FR-072K2L', '2.2k 1206', 10, 0.053, 0.04, 'backorder, due 2026-11-23', '1 used', 'keep'),
 ('311-220FRCT-ND', 'RC1206FR-07220RL', '220 1206', 10, 0.053, 0.04, 'in stock', '1 used', 'keep'),
 ('311-6.80KFRCT-ND', 'RC1206FR-076K8L', '6.8k 1206', 10, 0.056, 0.04, 'in stock', '2 used', 'keep'),
 ('311-15.0KFRCT-ND', 'RC1206FR-0715KL', '15k 1206', 10, 0.053, 0.04, 'in stock', '1 used', 'keep'),
 ('311-1.20MFRCT-ND', 'RC1206FR-071M2L', '1.2M 1206', 10, 0.053, 0.04, 'in stock', '1 used', 'keep'),
 ('311-47.0KFRCT-ND', 'RC1206FR-0747KL', '47k 1206', 10, 0.053, 0.04, 'in stock', '4 used', 'keep'),
 ('311-2.20FRCT-ND', 'RC1206FR-072R2L', '2.2 ohm 1206', 10, 0.091, 0.08, 'in stock', '1 used', 'keep'),
 ('311-18.0KFRCT-ND', 'RC1206FR-0718KL', '18k 1206', 10, 0.053, 0.04, 'in stock', '2 used', 'keep'),
 ('311-3.30FRCT-ND', 'RC1206FR-073R3L', '3.3 ohm 1206', 10, 0.086, 0.14, 'backorder, past due (was due 2026-11-09)', '2 used', 'keep'),
 ('311-100FRCT-ND', 'RC1206FR-07100RL', '100 ohm 1206', 10, 0.053, 0.04, 'in stock', '2 used', 'keep'),
 ('1276-1017-1-ND', 'CL31B104KBCNNNC', '100 nF 50 V X7R 1206', 20, 0.08, 0.04, 'in stock', '13 used', 'keep'),
 ('1.5KE20ALFCT-ND', '1.5KE20A', 'TVS 17.1 V 1500 W', 2, 1.06, 0.73, 'in stock', 'D101 + 1', 'keep'),
 ('1.5KE22ALFCT-ND', '1.5KE22A', 'TVS 18.8 V 1500 W', 2, 1.06, 0.74, 'in stock', 'D301 + 1', 'keep'),
 ('P6KE20ALFCT-ND', 'P6KE20A', 'TVS 17.1 V 600 W', 2, 0.70, 0.49, 'in stock', 'D401 + 1', 'keep'),
 ('P6KE22ALFCT-ND', 'P6KE22A', 'TVS 18.8 V 600 W', 4, 0.70, 1.22, 'in stock', 'D404-D406 + 1', 'keep'),
 ('P6KE24ALFCT-ND', 'P6KE24A', 'TVS 20.5 V 600 W', 2, 0.70, 0.49, 'in stock', 'D501 + 1', 'keep'),
 ('1N5817RLGOSCT-ND', '1N5817RLG', 'Schottky 20 V 1 A', 2, 0.67, 0.34, 'in stock', 'D402 + 1', 'keep'),
 ('2N3906FS-ND', '2N3906BU', 'PNP TO-92', 2, 0.28, 0.14, 'in stock', 'Q404 + 1', 'keep'),
 ('P14443-ND', 'EEU-FR1V681L', 'WRONG PART: 680 uF 35 V in a 10 x 25 mm can, 27 mm seated; the dev-kit tray allows 23 mm (review B1)', 4, 1.46, 0.44, 'in stock', '-', 'delete'),
 ('399-C1206C103K5RACTUCT-ND', 'C1206C103K5RACTU', '10 nF 50 V X7R 1206', 10, 0.124, 0.09, 'in stock', '1 used', 'keep'),
 ('311-1.00KFRCT-ND', 'RC1206FR-071KL', '1k 1206', 25, 0.0404, 0.08, 'in stock', '9 used', 'keep'),
 ('1276-1066-1-ND', 'CL21B105KAFNNNE', 'WRONG PART: 1 uF 25 V in 0805, added by mistake', 5, 0.11, 0.05, 'BACKORDER', '-', 'delete'),
 ('BAT85S-TAPCT-ND', 'BAT85S-TAP', 'Schottky 30 V DO-35', 4, 0.50, 0.74, 'in stock', 'D1001 D1002 + 2', 'keep'),
 ('F989-ND', '0297005.WXNV', 'mini blade fuse 5 A', 3, 0.39, 0.20, 'in stock', 'F401 F501 + 1', 'keep'),
 ('P14397-ND', 'EEU-FR1C102L', 'WRONG PART: 1000 uF 16 V in an 8 mm can with 3.5 mm lead spacing; C404 has 5.0 mm holes (review B1)', 2, 0.94, 0.19, 'in stock', '-', 'delete'),
 ('399-C1206C105K5RACTUCT-ND', 'C1206C105K5RACTU', '1 uF 50 V X7R 1206 (replaces TDK C3216X7R1H105K160AB: 0 in stock, due 2027-03-29)', 5, 0.46, None, 'in stock', 'C104 C603 C604 + 2', 'keep'),
 ('1528-5997-ND', '5997', 'Adafruit CH334F 4-port USB hub', 1, 4.95, None, 'in stock', 'MOD601', 'keep'),
 ('2183-2813-ND', '2813', 'Pololu pushbutton power switch', 1, 10.14, None, 'ships in about 1 day', 'MOD401', 'keep'),
 ('1528-1988-ND', '3142', 'WRONG PART: Adafruit jumper wires, added by mistake for the ribbon cable', 1, 3.95, None, 'in stock', '-', 'delete'),
 ('1528-5807-ND', '5807', 'Adafruit HUSB238 USB-C PD trigger', 1, 5.95, None, 'in stock', 'MOD501 (USB-C charging)', 'phase2'),
 ('P12417-ND', 'EEU-FM1V681', '680 uF 35 V, 12.5 mm can, 22 mm seated, 5.0 mm pitch (replaces EEU-FR1V681L; FM series, ripple rating not compared)', 4, 1.47, None, 'in stock: 1,548', 'C101 C102 C103 + 1', 'keep'),
 ('P12366-ND', 'EEU-FM1C102', '1000 uF 16 V, 10 mm can, 22 mm seated, 5.0 mm pitch (replaces EEU-FR1C102L)', 2, 1.07, None, 'in stock: 2,715', 'C404 + 1', 'keep'),
 ('1276-3387-1-ND', 'CL32B106KBJNNNE', '10 uF 50 V X7R 1210, cut tape (replaces the backordered Murata part)', 10, 0.428, None, 'in stock: 573,447', 'C301 C402 C403 C501 C702 + 5', 'keep'),
 ('P12408-ND', 'EEU-FM1V151', '150 uF 35 V, 8 mm can, 13 mm seated, 3.5 mm pitch. A VALUE CHANGE for C405 (was 220 uF): no 220 uF 35 V part in an 8 mm can was in stock', 2, 0.58, None, 'in stock: 32,224', 'C405 + 1', 'keep'),
]
DK_CART_SUBTOTAL_READ = 178.18     # what the cart showed with all 79 lines
DK_CART_TARIFF_READ = 28.75
DK_SHIP = 4.99                     # USPS Ground Advantage (FedEx or UPS Ground 8.49)

# Lines DigiKey would not take from a pasted list, to add by hand in the same cart.
# (what, qty, unit, basis, note)
DK_BY_HAND = [
 ('TL431 in TO-92 with straight leads (TI TL431ACLP)', 2, 0.50, 'est', 'U402 + 1; 0.14 at Mouser on 2026-10-24. Not the formed-lead TL431ACLPRE3'),
 ('1N5247B 17 V zener, DO-35', 2, 0.17, 'quote', 'D502 + 1; Mouser 2026-10-24'),
 ('4.7 ohm 0.6 W metal film axial (Vishay MBB02070C4708FCT00)', 2, 0.26, 'quote', 'R408 + 1; Mouser 2026-10-24'),
 ('C&K PTS645VL58-2 LFS right-angle tactile switch, or another PTS645V right-angle part', 2, 0.33, 'est',
  'SW401 + 1; the price is Mouser\'s through an aggregator, where it showed 0 in stock on 2026-11-09. Not checked at DigiKey'),
]

# ----------------------------------------------------------------------------- the other stage 1 carts
# (supplier, what, qty, unit, basis, note)
OTHER = [
 ('PCBWay', 'ATLAS-PWR-1 bare boards, 5 pcs: 130 x 84 mm, 4 layers, 2 oz outside, 1 oz inside, HASL lead-free', 1, 155.79, 'page',
  'instant quote read again 2026-11-09 (same as Oct 26). Not signed in at PCBWay, so it is not in a cart; the price is "subject to review" after the Gerbers are uploaded'),
 ('PCBWay', 'DHL to Fairfax, VA', 1, 26.55, 'page', 'instant quote 2026-11-09'),
 ('PCBWay', 'US import duty on the boards', 1, round(155.79 * PCB_DUTY, 2), 'est', '35 % of the board price; PCBWay shows its own figure at checkout'),
 ('PCBWay (reserve)', 'Second order of the same boards, only if the first has a mistake', 1, 155.79, 'page', 'the same instant quote, read 2026-11-09'),
 ('PCBWay (reserve)', 'DHL to Fairfax, VA', 1, 26.55, 'page', 'the same instant quote, read 2026-11-09'),
 ('PCBWay (reserve)', 'US import duty on the boards', 1, round(155.79 * PCB_DUTY, 2), 'est', 'same 35 %'),
 ('Amazon', 'JKBMS JK-B1A8S10P smart BMS, 3S-8S Li-ion, 100 A, Bluetooth (ASIN B0D148FGQB)', 1, 66.49, 'page',
  'in stock, free delivery Nov 10. Replaces the JBD 4S 100 A, sold out at 18650battery.com and 18650batterystore.com'),
 ('Hobbywing Direct', 'Hobbywing UBEC 10A V2 Car, SKU 30603003: 2-6S in, 6.0 / 7.4 / 8.4 V out, 10 A continuous', 1, 24.99, 'page',
  'replaces the Castle BEC 2.0 (46.95) and the Castle Link (26.99); the page does not show a stock count'),
 ('Hobbywing Direct', 'shipping', 1, 6.00, 'est', 'not read'),
 ('Small parts', 'Emergency-stop push button, normally closed, twist to release, 16 or 22 mm panel hole', 1, 9.99, 'est', ''),
 ('Small parts', 'MIDI bolt-down fuse 100 A with a holder', 1, 12.00, 'est', 'the fuse alone was 2.74 at Mouser on 2026-10-24'),
 ('Small parts', 'XT90-S anti-spark connector pair', 1, 6.00, 'est', 'plain XT90s are on the shelf (Progressive RC order 310320)'),
 ('Small parts', '10 AWG silicone wire, 1 m red and 1 m black', 1, 10.00, 'est', ''),
 ('Small parts', '16 and 18 AWG silicone wire, 2 m each colour', 1, 8.00, 'est', ''),
 ('Small parts', 'M5 ring terminals for 10 AWG, heat-shrink assortment', 1, 7.00, 'est', ''),
 ('Small parts', 'Pre-crimped JST PH and XH leads, Dupont housings and crimps (E-stop, FSESC COMM, J14 harness)', 1, 9.00, 'est', ''),
 ('Small parts', '40-wire IDC ribbon cable, 150 mm (Adafruit 1988)', 1, 4.00, 'est', '2.95 on 2026-10-24, unverified then too'),
 ('Small parts', 'USB leads: USB-A right-angle to USB-C 0.3 m, micro-USB to USB-A 0.3 m, micro-USB jack lead, panel-mount USB-C extension', 1, 22.00, 'est', 'never priced in rev B'),
 ('Small parts', 'M3 brass standoffs, 25 mm, 6 pcs (the 7 mm deck spacers are printed)', 1, 8.00, 'est', '7.99 for an Amazon assortment in September'),
 ('Small parts', 'M3 brass heat-set inserts, 50 pcs', 1, 9.00, 'est', 'screws come from the MISUMI gift'),
 ('Small parts', 'Kapton tape, zip ties, 3 mm plywood sheet 300 x 300 mm', 1, 12.00, 'est', ''),
 ('Small parts', 'JST-XH 5-pin balance-lead extension (pack balance plug to the BMS)', 1, 6.00, 'est', ''),
 ('Small parts', '32-pitch pinion, 15 tooth, 1/8 in (3.175 mm) bore, for the Puller Pro (docs/PERFORMANCE.md)', 1, 8.00, 'est',
  'only if the chassis does not already carry a 14 or 15 tooth pinion (checklist A4)'),
 ('Small parts', 'In-line mini blade fuse holders, 2, with a 10 A fuse (UBEC lead) and a 7.5 A fuse (latch lead)', 1, 8.00, 'est', 'review S8'),
 ('Small parts', 'LiPo charging bag', 1, 12.00, 'est', 'review B5'),
 ('Small parts', 'Servo extension leads, 3-pin, 2 (FSESC servo signal to J904, and a spare)', 1, 6.00, 'est', 'review B5'),
 ('Small parts', '24 or 26 AWG hookup wire in a few colours (latch ON and OFF, E-stop loop)', 1, 8.00, 'est', 'review B5'),
 ('Small parts', 'M3 nuts, M2.5 x 6 and M4 x 8 screws, if the MISUMI box has none', 1, 8.00, 'est', 'review B5'),
 ('SendCutSend (gift code)', '6061 bar 40 x 15 x 3 mm with three 3.2 mm holes, and the 3 mm acrylic FET shield', 1, 0.00, 'est',
  'paid from the 250.00 gift code (Aug 5 email), never used; confirm the code applied at checkout'),
]

# Bought only if section A of the checklist finds them missing. Not in the stage 1 total; BUDGET.md shows them beside it.
CONDITIONAL = [
 ('Hakko T15 soldering tips, 2', 28.00, 'if the irons have no tips and the school lab\'s are not free (A8)'),
 ('NVMe SSD, 250 to 500 GB, for the second Jetson', 45.00, 'if it has no storage of its own (A2)'),
 ('Motor sensor-lead adapter or a longer sensor lead', 8.00, 'if the Puller Pro\'s plug and the FSESC\'s socket differ (A4)'),
 ('Small-parts shipping from sellers that charge it', 15.00, 'the small-parts lines assume free shipping'),
]

# The same board at JLCPCB, read on 2026-11-09 with the Gerbers uploaded and saved to the cart there (no order placed).
JLC = dict(boards=90.79, parts='engineering fee 25.00, board 6.80, lead-free HASL 5.30, 2 oz outer copper 36.70, 1 oz inner copper 16.99',
           shipping=26.60, shipping_note='UPS Express Saver, duties-paid service, 2 to 4 business days')

# Phase 2: the built-in 18650 pack with USB-C charging. Priced, not in the stage 1 carts.
PHASE2 = [
 ('DigiKey', 'Adafruit 5807 USB-C PD trigger', 1, 5.95, 'cart', 'in the DigiKey cart now; leave it or move it to a later order'),
 ('eBay or Amazon', 'XL4015 CC/CV buck module, 5 A', 1, 8.00, 'est', 'generic; check its current-sense side on the bench (review B1)'),
 ('Anker', 'Anker 715 65 W USB-C charger (A2663)', 1, 29.99, 'quote', 'September 2026'),
 ('any', 'USB-C cable, 5 A e-marked, 1 m', 1, 10.00, 'est', ''),
 ('18650 Battery Store', 'Molicel P28A 18650, 12 + 2 spare', 14, 5.99, 'quote', '2026-09-26'),
 ('18650 Battery Store', 'shipping, lithium cells by ground', 1, 15.00, 'est', ''),
 ('any', 'Fish-paper rings, Kapton, 1 mm foam, 7-pin sense lead and NTC', 1, 22.00, 'est', 'September estimate'),
 ('eBay', 'Capacitor spot welder (Glitter 801D), only if no welder can be borrowed', 1, 304.51, 'quote', '2026-09-26, 269.51 + 35.00 shipping'),
]

# Sensor upgrade: the donated SICK TiM561 and LUCID Triton, later. Priced, not in the stage 1 carts.
SENSOR_UPGRADE = [
 ('DigiKey or Pololu', 'Pololu S18V20F12 12 V regulator for the Triton (MOD402)', 1, 29.95, 'quote', 'Pololu page 2026-10-24'),
 ('LUCID', 'GPIO-M8-5M-RA2-A camera power cable', 1, 40.00, 'quote', '2026-10-24'),
 ('ZimaSpace', 'USB 3 gigabit Ethernet adapter (RTL8153) for the lidar', 1, 9.90, 'quote', 'sale price 2026-10-24; list 15.90'),
]

# ----------------------------------------------------------------------------- shelf and credits
# (item, where it comes from, evidence, what to confirm by hand)
SHELF = [
 ('Traxxas Slash 4x4 chassis with the Holmes Hobbies Puller Pro 540 2200 kV motor', 'bought or donated for "car 2"', 'brief; atlas_knowledge.md section 6', 'the motor is fitted and turns; the sensor lead is in the box'),
 ('INJORA INJS235 servo', '"car 2"', 'brief', 'fits the Slash 4x4 servo bay; note the horn spline'),
 ('NVIDIA Jetson Orin Nano Super dev kit, 500 GB NVMe', 'car 1', 'brief; boots from NVMe since Oct 26', 'stays on car 1; not needed for car 1 v2'),
 ('Second Jetson Orin Nano on NVIDIA\'s dev-kit carrier', 'on hand', 'Ragini, Nov 9: "ready to go", "it\'s NVIDIA\'s dev kit"',
  'which module (Orin Nano 8 GB, Super firmware or not); what it boots from (an NVMe drive, or car 1\'s retired 256 GB SD card); JetPack version'),
 ('Flipsky FSESC, two units', 'car 1 and the spare', 'brief; Ragini Oct 24', 'which is the Mini 6.7 Pro and which the cased full-size unit (MEASURE_FIRST 21); the spare goes on the new chassis'),
 ('RPLidar C1', 'car 1', 'brief; atlas_knowledge.md section 5', 'the four M2.5 holes on its base: measure the pattern'),
 ('Luxonis OAK-D Pro', 'car 1', 'brief', 'the 1/4-20 thread under it; which IMU it reports (BNO086 or BMI270)'),
 ('4S LiPo packs', 'car 1', 'brief', 'for each pack: capacity, C rating, length x width x height, main connector, balance plug'),
 ('RC balance charger (iCharger X6), MEAN WELL 350 W supply, XT90 charge cables', 'Progressive RC, July', 'atlas_knowledge.md', 'charger sets up 4S LiPo balance charge'),
 ('2 panel-mount XT90 extension cables, 2 XT90 to bare-wire parallel cables, 3 XT90 connectors', 'Progressive RC order 310320, delivered Oct 14', 'order email Oct 9', 'wire gauge of the bare-wire cables (need 10 AWG for the board pigtail)'),
 ('Anderson Powerpole PP45: 30 red and 30 black housings, 60 contacts for 10-14 AWG', 'Anderson Power sample order 250322, shipped Sep 21', 'order acknowledgment Sep 15', 'whether the lab has a Powerpole crimper'),
 ('About 500 M3 x 10 screws plus 6 and 8 mm lengths', 'MISUMI', 'atlas_knowledge.md', '-'),
 ('Noctua fan', 'on hand', 'brief', 'model: the board header wants a 5 V PWM fan (NF-A4x10 5V PWM)'),
 ('Hakko FM206 station with two FM2027 irons', 'Hakko, August', 'atlas_knowledge.md', 'the kits came with no tips: T15 tips are needed unless the school lab irons are used'),
 ('Bambu P1S with PETG-CF, laser cutter, nickel strip', 'on hand', 'brief', 'laser sheet thickness (MEASURE_FIRST 27)'),
 ('RC4WD parts box', 'RC4WD, shipped Sep 4', 'email thread', 'contents unknown: the wish list had a servo, an ESC, a 2S pack, adapters, servo leads, hex drivers'),
 ('SICK TiM561 with its M12 cables, LUCID Triton with the Edmund Optics 4 mm lens, PoE injector', 'donated', 'brief; lens shipped Oct 27', 'kept for the sensor upgrade'),
 ('UGREEN 130 W and Omni 20+ power banks', 'car 1', 'brief', 'not used on car 1 v2'),
]

# (who, what, state, how it could help car 1 v2, counted in the totals?)
CREDITS = [
 ('SendCutSend', '$250.00 gift code, no expiry, reusable until spent', 'confirmed Aug 5, unused',
  'FET heatsink bar, acrylic shield, any laser-cut sheet parts', 'yes: those parts are 0.00 cash'),
 ('Protocase', '$500 in-kind manufacturing (Student Sponsorship Program)', 'confirmed Sep 8 and Nov 2; their contact is waiting for STEP files',
  'sheet-metal or machined parts: an aluminium deck plate, the canopy, the FET bar', 'no: nothing in stage 1 needs it'),
 ('OSH Cut', '50 % off the subtotal through 2026-12-31, reusable code', 'confirmed Jul 7 and Aug 21', 'laser-cut and bent sheet metal', 'no'),
 ('PCBWay Future Innovators', '$200 Individual Student Project support, plus a $10 account balance', 'confirmed Oct 22 for the two rev A orders; "confirm the final order details with the PCBWay contact"',
  'the rev B bare boards, if PCBWay moves the support to the new order', 'no: ask first'),
 ('Bay Area Circuits', 'bare boards up to $1,000, only for boards their website prices by itself; 10-day turn, we pay shipping', 'offered Oct 2; our Oct 2 quotes were never answered',
  'both board orders, if InstantDFM prices the 4-layer 2 oz board', 'no: needs a quote run and an email to Spencer'),
 ('Adafruit', '10 % educator code', 'Jun 30 and Jul 7', 'Adafruit parts bought direct', 'no'),
 ('Dassault Systemes', 'SOLIDWORKS Student Team sponsorship: 20 activations, expires 2028-07-31', 'approved Nov 9', 'CAD and Flow Simulation for docs/AERO.md', 'no cash value in the car'),
 ('Edmund Optics, LUCID, SICK, Hakko, MEAN WELL, MISUMI, Anderson, Progressive RC, RC4WD', 'hardware already received', 'see shelf.csv', 'see shelf.csv', 'yes: on the shelf'),
]


def money(x):
    return f'{x:,.2f}'


def main():
    # ---- DigiKey
    cart_total = sum(q * u for (_, _, _, q, u, _, _, _, _) in DK)
    keep = [r for r in DK if r[8] == 'keep']
    drop = [r for r in DK if r[8] == 'delete']
    ph2 = [r for r in DK if r[8] == 'phase2']
    keep_total = sum(r[3] * r[4] for r in keep)
    by_hand_total = sum(q * u for (_, q, u, _, _) in DK_BY_HAND)
    dk_merch = keep_total + by_hand_total
    # Tariff: DigiKey's own per-line figure where the cart showed one; its average rate on the lines that showed none
    # and on the by-hand lines, which are not in the cart yet.
    rate = DK_CART_TARIFF_READ / DK_CART_SUBTOTAL_READ
    dk_tariff = (sum(r[5] for r in keep if r[5] is not None) + rate * sum(r[3] * r[4] for r in keep if r[5] is None)
                 + rate * by_hand_total)
    dk_tax = SALES_TAX * (dk_merch + dk_tariff + DK_SHIP)
    dk_all = round(dk_merch, 2) + round(dk_tariff, 2) + DK_SHIP + round(dk_tax, 2)      # the row's cells add up

    with open(os.path.join(HERE, 'cart_digikey.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['action', 'digikey_pn', 'mfr_pn', 'what', 'qty', 'unit_usd', 'line_usd', 'digikey_tariff_estimate_usd',
                    'availability_2026-11-09', 'for'])
        for (pn, mpn, what, q, u, t, av, refs, act) in DK:
            w.writerow([act, pn, mpn, what, q, f'{u:.4f}', f'{q * u:.2f}', '' if t is None else f'{t:.2f}', av, refs])
        for (what, q, u, basis, note) in DK_BY_HAND:
            w.writerow(['add by hand', '', '', what, q, f'{u:.2f}', f'{q * u:.2f}', '', f'not in the cart ({basis})', note])

    # ---- other suppliers
    def group(rows):
        g = {}
        for (sup, what, q, u, basis, note) in rows:
            g.setdefault(sup, []).append((what, q, u, basis, note))
        return g

    other = group(OTHER)
    with open(os.path.join(HERE, 'cart_other.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['supplier', 'what', 'qty', 'unit_usd', 'line_usd', 'basis', 'note'])
        for (sup, what, q, u, basis, note) in OTHER:
            w.writerow([sup, what, q, f'{u:.2f}', f'{q * u:.2f}', basis, note])
    for name, rows in (('cart_phase2_18650_usbc.csv', PHASE2), ('cart_sensor_upgrade.csv', SENSOR_UPGRADE)):
        with open(os.path.join(HERE, name), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['supplier', 'what', 'qty', 'unit_usd', 'line_usd', 'basis', 'note'])
            for (sup, what, q, u, basis, note) in rows:
                w.writerow([sup, what, q, f'{u:.2f}', f'{q * u:.2f}', basis, note])
    with open(os.path.join(HERE, 'shelf.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['item', 'from', 'evidence', 'confirm by hand'])
        w.writerows(SHELF)
    with open(os.path.join(HERE, 'credits.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['who', 'what', 'state on 2026-11-09', 'use on car 1 v2', 'counted in the totals'])
        w.writerows(CREDITS)

    def sub(sup):
        return sum(q * u for (_, q, u, _, _) in other.get(sup, []))

    pcb1 = sub('PCBWay')
    pcb2 = sub('PCBWay (reserve)')
    bms = sub('Amazon')
    bms_tax = SALES_TAX * bms
    bec = sub('Hobbywing Direct')
    bec_tax = SALES_TAX * bec
    small = sub('Small parts')
    small_tax = SALES_TAX * small
    scs = sub('SendCutSend (gift code)')
    stage1 = dk_all + pcb1 + pcb2 + bms + bms_tax + bec + bec_tax + small + small_tax + scs

    p2 = sum(q * u for (_, _, q, u, _, _) in PHASE2)
    p2_tax = SALES_TAX * p2
    p2_all = p2 + p2_tax
    p2_no_welder = p2 - 304.51
    up = sum(q * u for (_, _, q, u, _, _) in SENSOR_UPGRADE)
    up_all = up * (1 + SALES_TAX)

    pending = sum(a for _, a in BANK_PENDING)
    expected = BANK_POSTED + pending

    def basis_sum(b):
        t = sum(q * u for (_, _, q, u, bb, _) in OTHER if bb == b)
        if b == 'cart':
            t += keep_total + sum(q * u for (_, q, u, bb, _) in DK_BY_HAND if bb == 'cart')
        else:
            t += sum(q * u for (_, q, u, bb, _) in DK_BY_HAND if bb == b)
        return t

    L = []
    A = L.append
    A('# Car 1 v2 budget')
    A('')
    A(f'Generated by `bom/car1v2/make_car1v2.py` on {TODAY}. Nothing has been ordered or paid. Not every price was read that day: '
      'the table "How firm each dollar is" says how much was.')
    A('')
    A('## Money in the bank')
    A('')
    A('Truthifi could not be read: the free plan had used 5 of its 5 daily credits (they reset at midnight Eastern). '
      'These are the figures from the brief, read from the U.S. Bank feed earlier the same day.')
    A('')
    A('| | USD |')
    A('| --- | ---: |')
    A(f'| U.S. Bank checking, posted | {money(BANK_POSTED)} |')
    for name, a in BANK_PENDING:
        A(f'| {name}, still to post | {a:+,.2f} |')
    A(f'| **Expected once those post** | **{money(expected)}** |')
    A('')
    A('The three debits were spent before this design and are not part of the 1,500: FS.COM was storage for a training '
      'computer, the Adafruit payment (55.50 in all) was filed under car parts on an assumption, and the purpose of the '
      'Micro Center charge is not recorded in the books.')
    A('')
    A('| | USD |')
    A('| --- | ---: |')
    A(f'| The most car 1 v2 may use | {money(CAP)} |')
    A(f'| Stage 1 (below), cash, no credit used | {money(stage1)} |')
    A(f'| Left under the cap after stage 1 | {money(CAP - stage1)} |')
    A(f'| Left in the account after stage 1 | {money(expected - stage1)} |')
    A('')
    A('## Stage 1: the car drives on a 4S LiPo we own')
    A('')
    A('Everything the car must have, plus battery telemetry, the IMU and one-cable debugging. '
      'The power board is the full rev B board; the three modules it does not need yet stay off it.')
    A('')
    A('| cart | merchandise | tariff or duty | shipping | sales tax (6 %, assumed) | total |')
    A('| --- | ---: | ---: | ---: | ---: | ---: |')
    A(f'| DigiKey, Web ID 379079317 (`cart_digikey.csv`) | {money(dk_merch)} | {money(dk_tariff)} | {money(DK_SHIP)} | {money(dk_tax)} | {money(dk_all)} |')
    A(f'| PCBWay, 5 bare boards | 155.79 | {money(155.79 * PCB_DUTY)} | 26.55 | 0.00 | {money(pcb1)} |')
    A(f'| PCBWay, reserve for a second board order | 155.79 | {money(155.79 * PCB_DUTY)} | 26.55 | 0.00 | {money(pcb2)} |')
    A(f'| Amazon, JK smart BMS | {money(bms)} | 0.00 | 0.00 | {money(bms_tax)} | {money(bms + bms_tax)} |')
    A(f'| Hobbywing Direct, servo BEC | 24.99 | 0.00 | 6.00 | {money(bec_tax)} | {money(bec + bec_tax)} |')
    A(f'| Small parts, any seller (`cart_other.csv`), all estimates | {money(small)} | 0.00 | in the estimates | {money(small_tax)} | {money(small + small_tax)} |')
    A(f'| SendCutSend, bar and shield | 0.00 (gift code) | 0.00 | 0.00 | 0.00 | 0.00 |')
    A(f'| **Stage 1** | | | | | **{money(stage1)}** |')
    A('')
    A('How firm each dollar is (every line of the carts before sales tax, so PCBWay\'s shipping and duty are in it; DigiKey\'s tariff and shipping are not):')
    A('')
    A('| basis | USD | meaning |')
    A('| --- | ---: | --- |')
    A(f'| cart | {money(basis_sum("cart"))} | in the DigiKey cart on {TODAY}, with stock shown |')
    A(f'| page | {money(basis_sum("page"))} | read on the product page on {TODAY} |')
    A(f'| quote | {money(basis_sum("quote"))} | an earlier quote (Mouser, Oct 24), not read again |')
    A(f'| est | {money(basis_sum("est"))} | an estimate: nobody has read a price for the exact item |')
    A('')
    A('The DigiKey cart as it stands holds 83 lines and shows '
      f'{money(DK_CART_SUBTOTAL_READ)} with a {money(DK_CART_TARIFF_READ)} tariff estimate. The script checks that its copy '
      f'of those lines adds to the same subtotal ({money(cart_total)}). Before checkout: delete {len(drop)} lines '
      f'({", ".join(r[0] for r in drop)}): four wrong parts (two added by mistake, and the two "L" capacitors the review found '
      'are the wrong size) and three backordered lines. Their four replacements were added to the cart today; '
      f'add the {len(DK_BY_HAND)} low-value lines marked "add by hand"; '
      f'and decide whether the PD trigger ({ph2[0][0]}) stays. '
      'Three kept lines are on short backorder (the red LED to Nov 16, the 2.2k resistor to Nov 23, the 3.3 ohm resistor past due).')
    A('')
    A('The cart buys the parts for one board, with spares of the cheap parts. PCBWay\'s smallest order is five bare boards, '
      'so four boards stay bare. Eight parts are bought once (U401, MOD401, MOD601, J409, J601, U601, J801, J1003): a second '
      'board would need those again.')
    A('')
    A('### The same boards at JLCPCB')
    A('')
    jlc_duty = JLC['boards'] * PCB_DUTY
    jlc_all = JLC['boards'] + JLC['shipping'] + jlc_duty
    A(f'Read on {TODAY} with the Gerbers uploaded: {money(JLC["boards"])} for five boards ({JLC["parts"]}) plus '
      f'{money(JLC["shipping"])} shipping ({JLC["shipping_note"]}). The duty was not shown before checkout; at the same assumed '
      f'35 % it is {money(jlc_duty)}, so about **{money(jlc_all)}** an order against {money(pcb1)} at PCBWay. That is '
      f'{money(pcb1 - jlc_all)} less per order, {money(2 * (pcb1 - jlc_all))} with the reserve order. The board is saved in the JLCPCB cart. '
      'The totals on this page still use PCBWay: it is the dearer of the two, and PCBWay has offered support that JLCPCB has not.')
    A('')
    A('### Only if the shelf check says so')
    A('')
    A('Not in the stage 1 total. Section A of `docs/CAR1V2_CHECKLIST.md` decides each one.')
    A('')
    A('| what | USD with tax | bought if |')
    A('| --- | ---: | --- |')
    cond = 0.0
    for (what, usd, why) in CONDITIONAL:
        A(f'| {what} | {money(usd * (1 + SALES_TAX))} | {why} |')
        cond += usd * (1 + SALES_TAX)
    A(f'| **All four** | **{money(cond)}** | stage 1 would then be {money(stage1 + cond)} |')
    A('')
    A('### If the estimates are wrong')
    A('')
    worse = (dk_all + (8.49 - DK_SHIP) * (1 + SALES_TAX)
             + 2 * (155.79 * 1.15 * (1 + 0.55) + 26.55 * 1.10)
             + bms + bms_tax + (24.99 + 10.00) * (1 + SALES_TAX) + small * 1.30 * (1 + SALES_TAX) + cond)
    A(f'A pessimistic stage 1: the PCB quote 15 % higher, duty at 55 % instead of 35 %, DHL 10 % higher, every small-parts '
      f'estimate 30 % over, DigiKey by FedEx, Hobbywing shipping at $10, and all four conditional items bought. That comes to '
      f'**{money(worse)}**, with the reserve board order included. It is under the cap by {money(CAP - worse)}. '
      f'Without the reserve order it is {money(worse - (155.79 * 1.15 * 1.55 + 26.55 * 1.10))}.')
    A('')
    A('## Priced, not in stage 1')
    A('')
    A('| what | USD with 6 % tax | note |')
    A('| --- | ---: | --- |')
    A(f'| Phase 2: built-in 18650 pack and USB-C charging (`cart_phase2_18650_usbc.csv`) | {money(p2_all)} | '
      f'{money((p2_no_welder) * (1 + SALES_TAX))} if a spot welder can be borrowed. September quotes, not read again. |')
    A(f'| Sensor upgrade: Triton and TiM561 wiring (`cart_sensor_upgrade.csv`) | {money(up_all)} | October quotes, not read again. |')
    def room(x):
        return f'{money(CAP - x)} under the cap' if x <= CAP else f'{money(x - CAP)} OVER the cap'
    A(f'| **Stage 1 + phase 2** | **{money(stage1 + p2_all)}** | {room(stage1 + p2_all)}, but only if every estimate holds. In the pessimistic case above it does not fit. Treat phase 2 as not yet affordable inside the cap |')
    A(f'| Stage 1 + phase 2 with a borrowed welder + sensor upgrade | {money(stage1 + p2_no_welder * (1 + SALES_TAX) + up_all)} | {room(stage1 + p2_no_welder * (1 + SALES_TAX) + up_all)} |')
    A(f'| Stage 1 + phase 2 + sensor upgrade | {money(stage1 + p2_all + up_all)} | {room(stage1 + p2_all + up_all)} |')
    A('')
    A('## Credits and sponsorships (from the admin@ mailbox, Nov 9)')
    A('')
    A('| who | what | state | use on car 1 v2 | counted above |')
    A('| --- | --- | --- | --- | --- |')
    for c in CREDITS:
        A('| ' + ' | '.join(c) + ' |')
    A('')
    A('If PCBWay moves its $200 support to the rev B board order, stage 1 falls to '
      f'{money(stage1 - 200)}. If Bay Area Circuits prices and sponsors the boards instead, both PCBWay lines '
      f'({money(pcb1 + pcb2)}) fall to shipping only. Neither is counted, because neither has been confirmed for this board. '
      'Gift codes and serial numbers are in the emails, not in this repository.')
    A('')
    open(os.path.join(HERE, 'BUDGET.md'), 'w').write('\n'.join(L))
    assert abs(cart_total - DK_CART_SUBTOTAL_READ) < 0.06, (cart_total, DK_CART_SUBTOTAL_READ)
    assert stage1 < CAP and worse < CAP
    fit_usd, off_usd = stage1_population()
    print(f'board population: {fit_usd:.2f} fitted, {off_usd:.2f} left off (rev B BOM prices of Oct 26)')
    print(f'DigiKey cart check: {cart_total:.2f} vs read {DK_CART_SUBTOTAL_READ:.2f}')
    print(f'stage 1 {stage1:.2f}; phase 2 {p2_all:.2f}; upgrade {up_all:.2f}; expected balance {expected:.2f}')


# Stage 1 population of the power board: the rev B board, same copper, with the
# plug-in modules for the camera's 12 V rail and USB-C charging left off.
STAGE1_NOT_FITTED = {
    'MOD402': 'camera 12 V regulator. Only the LUCID Triton needs it; the OAK-D Pro runs from USB.',
    'MOD501': 'USB-C PD trigger. Part of phase 2 (built-in pack with USB-C charging).',
    'MOD502': 'CC/CV charger module. Part of phase 2.',
}


def stage1_population():
    """Write power_board_stage1.csv from the rev B board BOM. Returns (fitted_usd, left_off_usd)."""
    src = os.path.join(HERE, '..', 'revb', 'power_board_bom.csv')
    rows = list(csv.DictReader(open(src)))
    out, fitted, left = [], 0.0, 0.0
    for r in rows:
        refs = r['refs'].split()
        dnp = r['dnp_refs'].split()
        off = [x for x in refs if x in STAGE1_NOT_FITTED]
        on = [x for x in refs if x not in STAGE1_NOT_FITTED]
        unit = float(r['unit_usd'])
        # a row whose quantity is not a count of references (the Pico's two header strips) keeps its quantity
        n_on = int(r['qty']) - len(off) if on else 0
        if on:
            out.append(['fit', n_on, ' '.join(on), r['value'], r['mpn'], r['assembly'], f'{unit * n_on:.2f}', ''])
            fitted += unit * n_on
        for x in off:
            out.append(['leave off', 1, x, r['value'], r['mpn'], r['assembly'], f'{unit:.2f}', STAGE1_NOT_FITTED[x]])
            left += unit
        for x in dnp:
            out.append(['leave off', 1, x, r['value'], r['mpn'], r['assembly'], '0.00',
                        'never fitted on this board (marked do-not-populate in the schematic and on the board)'])
    with open(os.path.join(HERE, 'power_board_stage1.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['stage1', 'qty', 'refs', 'value', 'part', 'assembly', 'revb_bom_usd', 'why'])
        w.writerows(out)
    total = sum(float(r['line_usd']) for r in rows)
    assert abs(fitted + left - total) < 0.02, (fitted, left, total)
    return fitted, left


if __name__ == '__main__':
    main()
