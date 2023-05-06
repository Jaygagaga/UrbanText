import shutil

import pandas as pd
import argparse
import os
import glob

def save_zip(df, zip_path):
    compression_options = dict(method='zip', archive_name=f'{zip_path}.csv')
    df.to_csv(f'{zip_path}.zip', compression=compression_options)
def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        "--file_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap',
        help="Local path where scraped reviews are",
    )

    parser.add_argument(
        '-r',
        "--root_directory",
        required=True,
        default='/Users/jie/UrbanText',
        help='Root directory of the project',
    )

    parser.add_argument(
        '-s',
        "--save_path",
        required=True,
        type=str,
        default='./Data/Reviews/GoogleMap/all_reviews',
        help="local path where you want to save your processed and combined dataset",
    )
    parser.add_argument(
        '-e',
        "--extension",
        required=True,
        type=str,
        default='csv',
        help="file extension",
    )

    args = parser.parse_args()#args=[]

    return args
def concat(csv_files):
    all_ = pd.DataFrame()
    for i in range(len(csv_files)):
        try:
            df = pd.read_csv(csv_files[i], encoding="utf-8")
            # df['keyword'] = csv_files[i].split('/')[-1].split('.')[0].split('_')[-1]
            all_ = all_.append(df)
        except:
            continue
    return all_
from nltk.tokenize import WordPunctTokenizer
text = "Reset your password; if you just can't remember your old one?"



def correct_space(doc):
    tokens = WordPunctTokenizer().tokenize(doc)
    lens = len(tokens)
    new_sent = ''
    for token in tokens:
        if token != "'":
            new_sent += token + ' '
        else:
            new_sent +=token
    return new_sent, lens
import zipfile

def main():
    args = parse_arguments()
    os.chdir(args.root_directory)
    print('Current root directory: ', os.getcwd())
    print('Reading and concatenating all street reviews in {}'.format(args.file_path))
    if 'zip' in args.file_path:
        reviews_df = pd.DataFrame()
        with zipfile.ZipFile(args.file_path) as z:
            for filename in z.namelist():
                if'__MACOSX' not in filename and filename.split('/')[-1] != '':
                    try:
                        df = pd.read_csv(z.open(filename),encoding="utf-8")
                        reviews_df = pd.concat([reviews_df, df])
                    except:
                        print('Cannot open file {}'.format(filename))
    elif 'csv' in args.file_path:
        csv_files =  glob.glob(args.file_path + '/*.csv')
        reviews_df = concat(csv_files)
    GM_sg = pd.read_csv('./Data/Reviews/GoogleMap_Singapore/all_reviews.csv')
    GM_sg_ = GM_sg[(GM_sg.street != 'Bishan Park') & (GM_sg.local_name != 'Bishan Park')]
    reviews_df = reviews_df[(reviews_df.street != 'Bishan Park') & (reviews_df.local_name != 'Bishan Park')]
    GM_sg_ = GM_sg_.drop_duplicates('review_id')
    GM_sg_=GM_sg_[[i for i in GM_sg_.columns if i in reviews_df.columns]]
    reviews_df = reviews_df.drop_duplicates('review_id')
    all_reviews = pd.concat([reviews_df,GM_sg_])
    # print('Total number of review texts is {}'.format(len(reviews_df)))
    all_reviews.review_text = all_reviews.review_text.astype(str)
    content = all_reviews.review_text.map(lambda x: correct_space(x)[0])
    all_reviews['review_text'] = content
    all_reviews['word_length'] =all_reviews.review_text.map(lambda x: correct_space(x)[1])
    all_reviews = all_reviews[all_reviews['word_length']>2]
    remove_local_name = [ 'Tools of Old Singapore','Prince Charles Cinema','Singapore Indoor Stadium',
                          'Parliament of Singapore','Marsiling Mall', '4GLte Unlimited Pocket Wifi in Singapore - pick up at 7Eleven Stores',
                          'Yang Club Singapore','Singapore Recreation Club',"Let's Go Cook Singapore" , "Ripley's Believe It or Not! Odditorium" ,
                          'Science Centre Singapore','Jalan Besar Stadium' , 'Telok Kurau Studios' ,'Queensway Shopping Centre'
                          'SG Accident Help Centre','JEN Singapore Tanglin by Shangri-La', 'SCDF 2nd CD Division',
                          'Singapore Rescue Training Centre Pte Ltd','The Singapore Lyric Opera Limited','Singapore Ballet Ltd (formerly Singapore Dance Theatre)',
                          'ibis budget Singapore Emerald',
                          'Centre for Climate Research Singapore', 'Sandy Island',
                          'Prime Car - Car Dealer Singapore','SPC Admiralty', 'Singapore Chinese Orchestra Co Ltd',
                          'Cold Storage Greenwood Avenue','Immanuel Fellowship Singapore','Citadines Mount Sophia Singapore',
                          'Singapore Institute for Clinical Sciences (SICS)','Singapore Bowling @ Rifle Range','SG Taps','ibis Budget Singapore Ametrine',
                          'CS Fresh @ Greenwich V', 'Buddhist College of Singapore','Singapore Malay Chamber Of Commerce & Industry (SMCCI @ Jalan Pinang)'
                          'DPS International School','Singapore Hainanese Chicken Rice', 'Nassim Hill Bakery Bistro Bar','Shangri-La Apartments, Singapore', 'Action For Singapore Dogs',
                          'Heart of Darkness Singapore',  'Singapore Swimming Club', 'Singapore Pools @ Siglap', 'Singapore Aquaculture Technologies Pte Ltd',
                           'Singapore Pools Lengkok Bahru Branch','Singapore Post - Simpang Bedok Branch', 'Singapore PickleBall Association',
                           'Singapore Taekwon-do Academy @ Taman Jurong', 'Singapore Institute of Hospitality', 'Piano Lessons Singapore',
                           'Singapore Institute of Power and Gas', 'Singapore Moutai Baijiu Pte Ltd', 'Raffles Institution', 'Singapore Pools (Fajar Shopping Centre Branch)',
                           'ARAB STREET RESTAURANT','NUS Business School','Singapore Medical Council',"Prince's Landscape Pte Ltd", 'Singapore Pools Main Branch',
                           'Singapore Post - Serangoon Central Branch','Singapore Raffles Music College', 'SIM Global Education', 'Chong Hoe Tong (Singapore Pools Authorised Retailer)',
                           'Singapore Pump Products Pte. Ltd.','Singapore Lee Clan General Assn', 'Casuarina Road Car Park','Singapore Pools @ NTUC FairPrice (Jurong East St 13)',
                           'Singapore Sinhala Buddhist Association','Singapore Law Firm | Hill Dickinson LLP', 'National Heart Centre Singapore', 'ST Residences Novena - Short Term Serviced Apartments In Singapore',
                          'Singapore Meditation 新加坡修心中心 Pusat Meditasi Singapura சிங்கப்பூர் தியானம்',
                           'Singapore Color Photographic Society','International Furniture Fair Singapore Pte Ltd','Star Cruises', 'Every Nation Singapore',
                           'Chatsworth Preschool - Piccadilly Campus','MSTS Asia Singapore',
                           'Embassy of Indonesia in Singapore or KBRI Singapura','TUGA Singapore - Portuguese Restaurant Wine & Gourmet Products',
                           'Singapore Pools (Jalan Tiga Branch)',
                           'KINGSWAY MEDICAL CLINIC (Clementi)', 'Singapore Precision Repair & Overhaul Pte Ltd',
                           'Teo Sook Cheng Agency (Singapore Pools Authorised Retailer)',  'RS EVENT CENTER (Rockschool Singapore)',
                           'Classical Realism SG - Art School Singapore', "Nicole's Flower: Cafe & Flower Delivery in Singapore",
                           'Secondary trail loop', 'Pa-Auk Meditation Centre','Yanmar Asia (Singapore) Corporation Pte Ltd','Civil Defence Academy',
                           'Singapore Aero Engine Services Pte Ltd','Seletar Club Road Carpark','Beng Huat Store', 'Singapore Expo Hall 2 & 3',
                           'Singapore Hobby Supplies Pte Ltd', 'Scania Singapore Pte Ltd (Senoko)', 'Singapore Media Academy', 'Cable Car','Singapore Radio & Industry Pte Ltd',
                           'Singapore Post - Lim Ah Pin Road Branch', 'Singapore Taekwon-do Academy @ Telok Blangah','EF International Language Campus - English courses in Singapore',
                           'Singapore Police Force','Singapore Youth Olympic Games Statue',"Singapore's Women's Clinic Clementi",
                          'Singapore Wind Tunnel Facility', 'Riway Team 37 Singapore','Singapore Post - Novena Branch',
                           'Singapore Buddhist Youth Mission', 'Singapore Cartons Pte Ltd','Bedok Industrial Park E', 'Singapore Post - Raffles Place Branch',
                           'Singapore Tamilian Assn', 'Jackway Convertor Industries Pte Ltd', 'Singapore Post - Yishun Central Branch', 'CS Fresh @ Altez',
                           'Singapore Ji Yang Cai Clan Assn', "Speakers' Corner",'Aik Chin Hin Machinery Co',
                           'Singapore Post - Potong Pasir Branch','SINGAPORE AIRLINES LTD','Immigration Services Singapore | Go Global Gem',
                           'Singapore Association Of The Visually Handicapped',  'Singapore - Johore Express Pte Ltd', 'Singapore Hok San Association',
                           'Seah Koon Huat - Bukit Merah View (Singapore Pools Authorised Retailer)',  'Swift Battery - Car Battery Replacement Company',
                           'The Shoppes at Marina Bay Sands', 'Singapore Pools @ NTUC FairPrice (Yishun Ring Rd)',
                           'Republic of Singapore Yacht Club','Singapore Yacht Charter',
                           'Singapore College Of Traditional Chinese Medicine','Singapore Pools (Empress Rd Branch)',
                           'Singapore Institute of Retail Studies',
                           'Singapore Pools Telok Blangah Crescent Branch', 'Singapore Pools @ NTUC FairPrice (Sengkang East)',
                           'Singapore Mobility Gallery', 'Singapore Veterinary Animal Clinic',
                           'Singapore Refining Company Private Limited', 'Tuas Crescent', 'The Hacienda',
                           'Singapore Thong Chai Medical Institution - Bedok Community Clinic', 'Singapore International Chamber Of Commerce',
                           'North London Collegiate School (Singapore)',  'Singapore Christian Home',
                           'Singapore Balloon Artist | Balloon Decoration Specialist | THAT Balloons', 'SINGAPORE EPSON INDUSTRIAL PTE LTD'
                           'nanatang : Bake house and Studio (Baking Class & Customised Cake Singapore)','Singapore Pools @ Cheers',
                           'Dusit Thani Laguna Singapore','Singapore Baptist Convention',
                           'Bar @ Lorong 13', 'Singapore–MIT alliance', "Singapore Pools (King George's Ave Branch)",
                           'Wildflower Studio - Art Jamming x Cat Cafe Singapore','Singapore Sports & Orthopaedic Services (SSOC) (新加坡育骨科诊所)',
                           'Singapore Institute of Technology (SIT@TP)',
                           'Swift Battery Specialist Singapore', 'Singapore Pools @ 7-Eleven',
                           'Singapore Pools (Gek Poh Shopping Centre Branch)','GR.iD (GR.iD Singapore)',
                           'Singapore Pools Authorised Retailer @ (7-Eleven)',
                          'Singapore Asahi Chemical & Solder Industries Pte Ltd',
                          'Singapore Hostel', 'Shinkendo Singapore (Cairnhill CC)',
                          'Singapore Pools (Clementi N3 Branch)', 'Little Elephant SG',
                          'Swift Battery Specialist', 'ISS International School',
                          'Marsiling Industrial Estate',
                          'ST Engineering Unmanned & Integrated Systems Pte Ltd','Singapore Pools Betting Centre (Rangoon)',
                           'The Singapore Wheelchair', 'Singapore Post - Killiney Road Branch',
                           'Singapore Emcee Donna Daniels', 'Singapore Pools @ NTUC FairPrice (Hougang Mall)', 'MeltedSG',
                           'Singapore Indian Association', 'Singapore Pools Betting Centre (The Majestic)', "Lloyd's Inn",
                           'Singapore Pools @ NTUC FairPrice (Bukit Panjang Plaza)',   'ibis budget Singapore Pearl', 'Singapore Kobe Pte Ltd',
                           "Marian's Lactation Boost (Lactation Cookies Singapore)",  'Singapore Island Cruise & Ferry Services | St John’s/Lazarus & Kusu',
                           'Singapore Pools (Jalan Batu Branch)', 'Singapore Polytechnic',
                           'Singapore Pools @ Prime Supermarket (Compassvale St)', 'Singapore Pools @ NTUC FairPrice (Yung Kuang Road)',
                           'Proterial Asia Pacific Pte. Ltd.','Kohler Singapore Pte Ltd','Prison Fellowship Singapore', 'Bears & Friends Singapore',
                           'Singapore Management University',  'Singapore Sepak Takraw Federation',
                           'ibis budget Singapore Imperial', 'Apnea42 Freediving (Singapore)',
                           'The Chinese Calligraphy Society Of Singapore', 'Singapore Pools @ NTUC FairPrice (Tampines St 83)',
                           'A Little CakeShoppe Singapore','Singapore Pools (Bukit Panjang Branch)',
                           'Singapore Post - Choa Chu Kang Central Branch', 'Singapore Pools (Commonwealth Crescent Branch)',
                           'EcoTrail Singapore''Singapore Pools @ NTUC FairPrice (Jurong Point Hypermart)',
                           'New Pasar Baru Enterprises',  'Singapore S F International Authorized Partner',
                           'Singapore Pools Authorised Retailer (Metro @ Woodlands Causeway Point)',
                           'MSD International GmBH (Singapore Branch)','APS Swim School Singapore Pte Ltd',
                           "St Margaret's Secondary School", 'Singapore Institute of Technology (SIT@RP)',
                           'Singapore Pools (Ang Mo Kio N6 branch)','Zenxin Organic Food Singapore @ Pasir Panjang',
                           'Singapore Hin Ann Huay Kwan', 'Singapore Foochow Association', 'Singapore Pools @ Sheng Siong Supermarket (Tanglin Halt)',
                           'Radhasoami Satsang Beas Singapore', 'Registry of Marriages','Studio Asobi - Pottery Studio in Singapore', 'SPC Sengkang',
                           'PAUL SINGAPORE PTE LTD', 'Singapore Pools (Jurong West N5 Branch)','Singapore Badminton School',
                           'Singapore Fried Hokkien Mee 新加坡炒福建虾面','Singapore Tourism Board', 'Academy of Singapore Teachers',
                           'Singapore Mariners’ Club at the Maritime House',
                           'Singapore Pools @ NTUC FairPrice (Tampines Mall)',
                           'Singapore Highpolymer Chemical Products Pte Ltd','Singapore Counselling Centre',
                           'Singapore Buddhist Federation (SBF)','Chng Siow Eng Agency', 'Singapore Pools Silat Ave Branch', 'BusinessForSale.sg',
                           'Harmony Music School Singapore', 'Singapore Heart Foundation Heart Wellness Centre @ Bukit Gombak',
                           'Singapore Pools Authorised Retailer', 'Pâtisserie CLÉ | Tarts Singapore',
                           'Federation Of Art Societies (Singapore)', 'Singapore Buddhist Free Clinic (Dover)', "The Men's Club",
                           'Brighton College (Singapore)', 'Singapore Examinations and Assessment Board',
                           'Singapore Salvage Engineers Pte Ltd', 'Singapore Innovation Technology Pte Ltd',
                           'Singapore Post - Marine Parade Branch','Singapore Asia Publishers Pte Ltd', 'Multi-Storey Car Park H',
                           'ADVANCED HOMEOPATHIC CLINIC', 'Meiden Singapore Pte Ltd', 'Ai Cafe Singapore - Best Cafe Singapore',
                           'Hilton Garden Inn Singapore Serangoon',  'Jun Tennis Academy | Tennis Lessons Singapore',
                           'Healthway Medical (Bukit Batok)', 'Starke Singapore Pte. Ltd.',
                           'Singapore-Johore Express (Pte) Ltd Queen St Terminal',
                           'One World International School in Singapore',
                           'Singapore International Preschool','Mercedes-Benz Authorised Service Center (Pandan Loop)','Singapore Mass Rapid Transit Ltd-Fcs Dept',
                           "JYC @ Children's Society", 'Singapore Nursing Board',
                           'Teo Khar Bee Agency', '1-Net Singapore','Singapore Pools @ NTUC FairPrice (Bedok North St 4)',
                           'NTU Centre for Contemporary Art Singapore',  'Chef Works & Bragard Singapore (Chef Clothing)',
                           'Singapore Airport Terminal Services Workers Union',
                           'Marang Road Car Park', 'Singapore Environment Council', 'Singapore Blinds',
                           'Singapore After-Care Association','Cable Source – #1 Electrical Cable Supplier & Distributor In Singapore',
                           'Singapore Pools (Tampines N4 Branch)', 'Nippon Paint Singapore',
                           'InterContinental Singapore Robertson Quay, an IHG Hotel','Wilson Parking Singapore',
                           'Holiday Inn Singapore Orchard City Centre, an IHG Hotel',
                           'Rivière by Frasers Property Singapore','Singapore Post - Post Box', 'Ang mo kio Central 2 car park',
                           'Avila Catholic Shop Singapore','Singapore Pools @ NTUC FairPrice (Marine Parade Central)',
                           'Singapore Post - Jurong West Branch','The Embassy of Israel in Singapore',
                           'Singapore Pools @ NTUC FairPrice (Warehouse Club - FairPrice Hub)',
                           'Thailicious Boat Noodles - Singapore',
                           'Singapore Hokkien Huay Kuan Cultural Academy','Automobile Association of Singapore (AA Centre) - Car Towing, Assistance, Insurance & More',
                          'Cartoon.SG - Caricature Artists Singapore',
                          'SAF Yacht Club','Singapore Canoe Federation', 'Singapore -Johor Taxi Service',
                           'Guardian Health & Beauty - Kembangan MRT','Singapore Jin Hoe Lian Ghee Sia',
                           'Singapore Post - Crawford Branch', 'Ellington Square Playground',
                           'Singapore Paincare TCM Wellness','Burghley ActiveSG Squash & Tennis Centre',
                           'VictoriaHan Studio - Makeup Artist Singapore | For Weddings, Photoshoots & Commercial Events',
                           'Singapore Electric by Gimmelovetattoo','North Link Building','Singapore Polytechnic Gate 1',
                           'Singapore Passport Collection', 'Spring Cleaning Singapore', 'Eastern Lagoon I',
                           'Singapore Chung Hwa Medical Institute',
                           'Singapore Post - Harbourfront Centre Branch', 'Carlton City Hotel Singapore',
                          'Singapore Pools @ 7-Eleven (Circular Road)',
                          'Singapore Pools (Bishan N1 Branch)',
                          'Singapore Pools @ 7-Eleven (Sixth Avenue)',
                          'Singapore Luxury Homes - Property Consultants in Luxury Homes in Singapore',
                          'Singapore Marriott Tang Plaza Hotel', 'Pet Lovers Centre - Holland Village',
                          'Cold Storage West Coast Plaza','DIRECT CONTRACTOR SINGAPORE | Home Renovation | Choose Direct Contractor SG',
                          'Singapore Quality Institute',
                          'ibis budget Singapore Ruby', 'TVH | Singapore (Old Location)'
                           'Singapore Pools (Hougang N3 Branch)', 'Singapore Post Mailbox',
                           'Singapore Piano Teacher - Ms Liew',
                           'Singapore School of Samba', 'Singapore Weightlifting Federation',
                           'Singapore Post - Bukit Timah Branch',"Singapore Women's Clinic (Tampines)",
                           'Singapore Buddhist Free Clinic (Redhill Branch)', 'Singapore Institute Of Materials Management',
                           'Singapore Jain Religious Society',
                           'Margaret Drive Chicken Rice',
                           'Singapore Trading Centre', 'Big Boss Singapore','River Valley High School','Singapore Pools @ Yishun Blk 415 (N4 Branch)',
                           'Singapore Buddhist Youth Mission 新加坡佛教青年弘法','ibis Styles Singapore Albert','3house Homestay Accomodation|Guardianship Singapore',
                           'The Singapore Buddhist Lodge', 'Singapore Pools @ NTUC FairPrice (Dawson Place)','The Math Lab Singapore',
                          'The Singapore Ants Museum', 'GR.iD (GR.iD Singapore)','Civil Service College Singapore',
                          'Singapore Pools Authorised Retailer @ (7-Eleven)', 'Singapore Airlines', 'Singapore Bus Charter',
                           'Gyoza no Ohsho Singapore', 'Whitley Road Big Prawn Noodle',
                           'AlcoholNowSG Vending', 'Singapore Pub Crawl',
                          'Vigeo: Personal Health & Fitness Trainer In Singapore For Age Above 35',
                          'Singapore Distillery', 'Elyon Family Clinic & Surgery Pte Ltd - STD Clinic Singapore',
                           'Aardwolf Pestkare (S) Pte Ltd - Pest Management Services Singapore','Cheap Aircon Service Singapore',
                           'Singapore Chess Social', 'Singapore Every Home Crusade Co Ltd','Singapore Buddhist Meditation Centre',
                           'JVCKenwood Singapore Pte. Ltd.','Singapore Post - Macpherson Road Branch',
                           'Media Ministry of Cru Singapore', 'Energizer Singapore Pte Ltd',
                           'Technology Centre for Offshore and Marine, Singapore','Singapore Pools (Clementi Town Centre Branch)',
                           'Holiday Inn Singapore Little India',
                           'Tong aik huat (Singapore pools Authorised Retailer)',
                           'Singapore Safety Glass',
                           'Singapore Taekwon-do Academy @ Tiong Bahru',
                           'Singapore Pools @ Sheng Siong Supermarket (Marsiling Mall)',
                           'Singapore Cab Booking Pte Ltd', 'Singapore Post - Tanglin Branch',   'United Singapore Builders Pte. Ltd.'
                           'Singapore Buddhist Free Clinic (Tampines)','Ong Eng Siang Trading (Singapore Pools Authorised Retailer)',
                           'Singapore Pools @ 7-Eleven (Clementi St 11)','Fort Road Carpark','Singapore National Wushu Federation',
                           '6oz Espresso Bar @ Change Alley Mall','川苑酒家 chuan garden restaurant', 'Singapore Best Crispy Prata',
                           'Singapore Post - Bukit Panjang Branch','Shangri-La Residences, Singapore', 'SHATEC',
                           'Singapore Curtains and Blinds', 'Tai Seng',
                           'S&G Pool Renovations LLC',
                           'Singapore Primary School Science Tuition Centre - The Pique Lab',
                           'SINGAPORE STAINLESS STEEL PTE. LTD.','Murata Electronics Singapore (Pte) Ltd - Tuas',  'Singapore Aesthetic Centre', 'Singapore Pools (Lorong Lew Lian Branch)',
                           'International Community School (Singapore)', 'Toa Payoh Industrial Park', 'Uncle DiDi - Popcorn Shop & Pre Packaged Cotton Candy in SG',
                           'Wenzhou Clan Association Of Singapore','Singapore Judo Club','Singapore Apartment',
                           'Central Singapore Joint Social Service Centre',
                           'Renodots Singapore - Best Renovation Platform for Property Owners',
                          'Asia Tattoo Supply','Singapore General Hospital','Singapore Bus Academy',  'Singapore Pools Betting Centre (China Square)',
                          'Car Rental Singapore | ABC Rent-A-Car Pte Ltd', 'Singapore Thong Chai Medical Institution - Chin Swee Rd (Headquarters)',
                          'Shinnyo-en Singapore', 'Woodlands Industrial Park E','Singapore Pools @ NTUC FairPrice (Downtown East)','Yishun Swimming Lessons | Singapore Swimming Academy',
                            'K-Talyst Pte Ltd - Singapore Motiva Breast Implants Distributor', 'Ling Ling by The Wine Company', 'LaJiangShan Hotpot',
       'NotarySingapore', 'Singapore Buddhist Mission (www.sbm.sg)', 'Singapore Top Immigration',
       'Singapore Pools (Teban Gardens Branch)','Li Thoe Trading (Singapore Pools Authorised Retailer)',
       'Singapore Federation of Chinese Clan Associations 新加坡宗乡会馆联合总会','Singapore Pools @ Cheers (Haig Rd)',
       'Singapore Centre for Environmental Life Sciences Engineering', 'Singa Plastics Ltd', 'Camp Christine (Girl Guides Singapore)',
       'Hotel NuVe Heritage, City Hall', 'Singapore Chess Federation',
       'National Training Centre (Singapore Taekwondo Federation)',
       "Singapore Men's Health Clinic", "Methodist Girls' School", 'Singapore Pools Authorised Retailer (Prime Supermarket)',
       'Singapore Pools @ Giant Supermarket (Paya Lebar Square)','HDB Window Repair Singapore - Handle, Hinge, Latch, Gasket & Rubber Seal Replacement',
       "St. Joseph's Institution", 'Garry Doolan Golf Lessons Singapore', 'Singapore Pools (Jurong East Branch)',
       'Singapore Golf Association', 'Ja Lan Tiong Pte Ltd', 'Pet Cremators SG Singapore Pet Cremation',
       'Vertical Institute - Data Analytics, Digital Marketing & UX Design Courses In Singapore',
       'Singapore Housing Company', 'Le Imperial Singapore Pte Ltd',
       'Singapore Shwe Store','Singapore Takada Industries Pte Ltd',   'Singapore National Eye Centre SNEC',
       'Singapore Visitor Centre Rest Bugis Hotel','SMU Yong Pung How School of Law',
       'Embassy of Japan in Singapore',  'Soka Peace Centre','Singapore Pools @ 7-Eleven (Eunos Crescent)','Almond Spa@31 Holland Close',
       'Singapore Indian Fine Arts Society', 'Asia Safety Window Systems',  'Wellaholic (Farrer Road)',"Let's Go Cook Singapore",
       'Chix Hot Chicken | Nashville Hot Fried Chicken Singapore', 'Wanrise (Singapore Pools Authorised Retailer)',
       'RUF Automobile Singapore (Specialised Automobile)','PSA Singapore - Multipurpose Terminal',
       'Jalan Besar Sports Centre', 'Singapore Adoption Agency','Mastercool - Aircon Servicing Singapore',
       'Jurong Island Fire Station',   'Singapore Pools @ 7-Eleven (Owen Road)', 'Jalan Besar Stadium',
       'Singapore Pools @ NTUC FairPrice (Hillion Mall)',
       'SMU School of Computing and Information Systems 1','Swiss Club Singapore', 'GolfX SG',
       'Singapore Pools', 'Singapore Post Kallang Delivery Base',
       'VIVACE MUSIC SCHOOL SINGAPORE',
       'Singapore University of Social Sciences',
       'Singapore Pools (Tampines Mart Branch)', 'Singapore Gujarati Society',
       'Woodlands Ring Primary School', 'Singapore Contractors Association Ltd', 'National Institute of Education (NIE), Singapore',
       'Singapore Post - Serangoon Garden Branch', 'Singapore Gold Mart', 'Singapore Buddhist Free Clinic (Tanjong Pagar Branch)',
       'ibis budget Singapore West Coast','Kimberly-Clark Asia Pacific Pte Ltd',
       'Singapore Lam Ann Association (Building) 新加坡南安會館','Woodlands North Plaza', 'お好み焼き居酒屋 まかん Makan Japanese restaurant',
       'Hon Kah Trading (cyclinglesson.sg)', 'Singapore Wines Wholesales','Singapore Sustainability Academy',
       'Singapore Siong Lim Lotus Society',  'Singapore Institute of Architects', 'Singapore Planned Families Association',
       'Ming Zai Handmade Noodles Singapore','Singapore Swim School @ Swim Classes',
       'Singapore Estate Agency Pte Ltd',   'Singapore Red Cross Academy @ Red Cross House', 'Traditional Archers Singapore',
       'Singapore Pools @ NTUC FairPrice (Sun Plaza - Sembawang)',
       'Singapore Pools (Canberra Link Branch)',   'Singapore Underwater Federation',
       'Singapore Food Agency','Singapore Post - Ang Mo Kio Central Branch', 'Coverall (Singapore) Pte Ltd', 'Singapore Food Industries Ltd',
       'Dakshaini Silks: Singapore’s Premiere Silk Saree Emporium',  'St. John’s - St. Margaret’s Nursing Home',
       'Singapore Post - Bedok Central Branch',
       'Singapore Attractions Express',
       'Singapore Centre for Chinese Language',
       'JML Singapore Pte Ltd',    'JR Fitness Singapore (Bugis)',
       'Singapore Taekwon-do Academy @ Marine Parade CC',
       'Singapore Sindhi Association',
       'Holiday Inn Express Singapore Orchard Road, an IHG Hotel',
       'Singapore Post - Katong Branch', 'Liebherr-Singapore Pte. Ltd.',
       'Singapore Pools (Bukit Batok Central Branch)',
       "Sunbeam Place @ Children's Society",
       'Singapore Post - Tanjong Pagar Branch', 'Acts Church Singapore',
       'Singapore Post - Siglap Branch',   'Singapore Brain-Spine-Nerves Center',
       'Singapore Buddhist Welfare Service',
       'The Elephant Room Singapore', 'Singapore Post - Post Box 65018',
       'Singapore Physio',
       'BestOfMe – Asian-Based Digital Coaching Platform In Singapore For Your Empowerment',
       'Singapore Polish Grind', 'Singapore Post - Jurong East Branch',
       'Singapore Hui Ann Association',  'Whipper Tennis Academy', 'Singapore Scout Association',
       'Ang Mo Supermarket', 'ACS International',
       'Singapore Chinese Chamber of Commerce & Industry', 'SG Accident Help Centre', 'Singapore Malay Chamber Of Commerce & Industry (SMCCI @ Jalan Pinang)',
                          'The Great Room One George Street - Coworking Space & Hot Desking Singapore', 'DPS International School', 'Singapore Malay Chamber Of Commerce & Industry (SMCCI @ Jalan Pinang)',
                          'Ang Mo Kio Industrial Park 2', 'COSWAY UPPER BOON KENG ROAD SINGAPORE' , 'TriLab Singapore - Retul BikeFit' , 'Siltronic', 'Singapore Bao', 'Singapore Coffee', 'SCDF 4th Division HQ',
                          'Singapore Symphony Orchestra', 'FairPrice Compassvale Link', 'Dynacast Singapore', 'Singapore Carpentry','Singapore Buddhist Free Clinic (Tampines)','Changi Lorong 108 Fei Lao Seafood',
                          'Museum of Independent Music Singapore', 'Just Married Films (Singapore Wedding Photography, Videos & Photo)', 'Singapore Flyer Multi Storey Car Park' ,'United Singapore Builders Pte. Ltd.' ,
                          'nanatang : Bake house and Studio (Baking Class & Customised Cake Singapore)', 'Sofitel Singapore Sentosa Resort & Spa', 'Singapore Freelance Zone','Cold Storage Sentosa Cove',
                          'Bukit Timah Nam Sang Clinic', 'Maxwell Reserve Singapore, Autograph Collection', 'SINGAPORE EPSON INDUSTRIAL PTE LTD','Joo Chiat Rd','Singapore First Aid Training Centre Pte Ltd',
                          'Alliance Française de Singapour', 'Bef Pasir Ris St 53','SINDA', 'SPC Jalan Leban', 'Kimly Coffeeshop (Blk 131 Marsiling Rise)','JKA Singapore', 'TVH | Singapore (Old Location)',
                          'Singapore Pools (Hougang N3 Branch)','Singapore Wine Vault', 'Outward Bound Singapore (Reception and Activity Centre)','The Patio SG'
                          ]
    all_reviews_ = all_reviews[~all_reviews.local_name.isin(remove_local_name)]
    print('Total number of reviews with texts longer than 2 words after removing obvious indoor places is {}'.format(len(all_reviews_)))
    print(all_reviews_.local_name.unique())
    batch_size = int(len(all_reviews_)/3)
    import math
    for batch_idx in range(math.ceil(len(all_reviews_) / batch_size)):
        text_batch = all_reviews_.iloc[batch_size * batch_idx:batch_size * (batch_idx + 1)]
        # break
        text_batch['index'] = range(0,len(text_batch))
        divided_by = int(len(text_batch)/3)
        lighttag_page_index = []
        for i in range(divided_by+1):
            lighttag_page_index += [i]*3
            # print(lighttag_page_index +[i]*3)
        text_batch['lighttag_page_index'] = lighttag_page_index[:len(text_batch)]

        if args.extension == 'zip':
            save_zip(text_batch,'./Data/Reviews/TripAdvisor_Singapore/'+'TripAdvisor_SG_processed_team{}'.format(batch_idx))
        if args.extension == 'csv':
            text_batch.to_csv('./Data/Reviews/TripAdvisor_Singapore/'+'TripAdvisor_SG_processed_team{}.csv'.format(batch_idx))
        print('Saved processed csv file in {}'.format(args.save_path))

if __name__ == '__main__':
    main()


