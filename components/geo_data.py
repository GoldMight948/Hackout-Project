"""
Geographical data dictionary mapping countries to their respective states/provinces/territories.
Used for dynamic dropdown selection during business profile registration and company setup.
"""

COUNTRY_STATE_DATA = {
    "India": [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi (NCT)", "Chandigarh", "Jammu and Kashmir", "Ladakh", "Puducherry"
    ],
    "United States": [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
        "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
        "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
        "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
        "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
        "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ],
    "Germany": [
        "Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen",
        "Hamburg", "Hesse", "Lower Saxony", "Mecklenburg-Vorpommern",
        "North Rhine-Westphalia", "Rhineland-Palatinate", "Saarland", "Saxony",
        "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"
    ],
    "United Kingdom": [
        "England", "Scotland", "Wales", "Northern Ireland",
        "Greater London", "West Midlands", "Greater Manchester", "West Yorkshire"
    ],
    "Canada": [
        "Alberta", "British Columbia", "Manitoba", "New Brunswick",
        "Newfoundland and Labrador", "Nova Scotia", "Ontario",
        "Prince Edward Island", "Quebec", "Saskatchewan",
        "Northwest Territories", "Nunavut", "Yukon"
    ],
    "Australia": [
        "Australian Capital Territory", "New South Wales", "Northern Territory",
        "Queensland", "South Australia", "Tasmania", "Victoria", "Western Australia"
    ],
    "France": [
        "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Brittany",
        "Centre-Val de Loire", "Corsica", "Grand Est", "Hauts-de-France",
        "Île-de-France", "Normandy", "Nouvelle-Aquitaine", "Occitanie",
        "Pays de la Loire", "Provence-Alpes-Côte d'Azur"
    ],
    "Japan": [
        "Aichi", "Chiba", "Fukuoka", "Fukushima", "Gifu", "Gunma", "Hiroshima",
        "Hokkaido", "Hyogo", "Ibaraki", "Kanagawa", "Kyoto", "Mie", "Miyagi",
        "Nagano", "Niigata", "Osaka", "Saitama", "Shizuoka", "Tochigi", "Tokyo"
    ],
    "China": [
        "Anhui", "Beijing", "Chongqing", "Fujian", "Gansu", "Guangdong",
        "Guangxi", "Guizhou", "Hainan", "Hebei", "Heilongjiang", "Henan",
        "Hubei", "Hunan", "Inner Mongolia", "Jiangsu", "Jiangxi", "Jilin",
        "Liaoning", "Ningxia", "Qinghai", "Shaanxi", "Shandong", "Shanghai",
        "Shanxi", "Sichuan", "Tianjin", "Tibet", "Xinjiang", "Yunnan", "Zhejiang"
    ],
    "Singapore": [
        "Central Region", "East Region", "North Region",
        "North-East Region", "West Region"
    ],
    "Brazil": [
        "Amazonas", "Bahia", "Ceará", "Distrito Federal", "Espírito Santo",
        "Goiás", "Maranhão", "Mato Grosso", "Minas Gerais", "Pará", "Paraná",
        "Pernambuco", "Rio de Janeiro", "Rio Grande do Sul", "Santa Catarina", "São Paulo"
    ],
    "Mexico": [
        "Aguascalientes", "Baja California", "Chihuahua", "Coahuila",
        "Guanajuato", "Hidalgo", "Jalisco", "Mexico City", "Morelos",
        "Nuevo León", "Puebla", "Querétaro", "San Luis Potosí", "Sinaloa",
        "Sonora", "State of Mexico", "Tamaulipas", "Veracruz", "Yucatán"
    ],
    "Other": [
        "General / Headquarters Region",
        "National Capital Region",
        "Northern Territory / Province",
        "Southern Territory / Province",
        "Eastern Territory / Province",
        "Western Territory / Province",
        "Central District",
        "Offshore / Remote Operations"
    ]
}

def get_country_list():
    """Return sorted list of countries."""
    countries = list(COUNTRY_STATE_DATA.keys())
    if "Other" in countries:
        countries.remove("Other")
        countries.sort()
        countries.append("Other")
    else:
        countries.sort()
    return countries

def get_states_for_country(country: str):
    """Return list of states/provinces for given country."""
    return COUNTRY_STATE_DATA.get(country, COUNTRY_STATE_DATA["Other"])
