import sqlite3
DB="data.db"
career=[
("1993","भारतीय जनता पार्टी","Bharatiya Janata Party","सक्रिय रूप से जुड़े; युवा मोर्चा मंडल उपाध्यक्ष रहे।","Joined actively; served as Yuva Morcha Mandal Vice-President."),
("1998","जिला कार्यसमिति","District Working Committee","जिला कार्यसमिति सदस्य।","Member, District Working Committee."),
("2001","हिन्दू जागरण संघ","Hindu Jagran Sangh","जिला महामंत्री।","District General Secretary."),
("2004","हिन्दू जागरण मंच","Hindu Jagran Manch","जिला अध्यक्ष।","District President."),
("2009","लोकसभा चुनाव","Lok Sabha Election","अम्बेडकरनगर लोकसभा के सह संयोजक।","Co-coordinator for Ambedkar Nagar Lok Sabha."),
("2013","बसखारी मंडल","Baskhari Mandal","जिला प्रतिनिधि एवं दूसरी बार जिला कार्यसमिति सदस्य।","District representative and second-time District Working Committee member."),
("2014","लोकसभा चुनाव","Lok Sabha Election","टांडा विधानसभा के चुनाव समन्वयक।","Election coordinator for Tanda Assembly."),
("2016","भारतीय जनता पार्टी","Bharatiya Janata Party","जिला महामंत्री।","District General Secretary."),
("2017","विधानसभा चुनाव","Assembly Election","जिले के चुनाव संयोजक।","District election coordinator."),
("2018","स्थानीय निकाय / BJP","Local Body Elections / BJP","नगरपालिका/नगरपंचायत चुनाव जिला संयोजक; BJP जिला उपाध्यक्ष।","District coordinator for municipal elections; BJP District Vice-President."),
("2019","लोकसभा / उपचुनाव","Lok Sabha / By-election","आलापुर विधानसभा प्रभारी; जलालपुर विधानसभा उपचुनाव संयोजक।","In-charge of Alapur Assembly; coordinator for Jalalpur Assembly by-election."),
("2023","सहकारिता चुनाव","Cooperative Elections","जिले के चुनाव संयोजक।","District election coordinator."),
("2024","लोकसभा चुनाव","Lok Sabha Election","लोकसभा चुनाव एवं लोकसभा प्रवास योजना में अकबरपुर विधानसभा प्रभारी।","In-charge of Akbarpur Assembly for Lok Sabha election and Pravas Yojana.")
]
con=sqlite3.connect(DB)
con.executescript("CREATE TABLE IF NOT EXISTS career(id INTEGER PRIMARY KEY AUTOINCREMENT,year TEXT,title_hi TEXT,title_en TEXT,description_hi TEXT,description_en TEXT);")
con.executemany("INSERT INTO career(year,title_hi,title_en,description_hi,description_en) VALUES(?,?,?,?,?)",career)
con.commit();con.close()
print("seeded")
