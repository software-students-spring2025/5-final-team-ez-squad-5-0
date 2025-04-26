import random
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from .. import mongo

quiz_bp = Blueprint('quiz', __name__)

# Get questions from existing list (simplified version for clarity)
QUIZ_QUESTIONS = [
    {"text": "Would you rather have a cat or a dog?", "options": ["Cat", "Dog"], "tag": "pets" },
    {"text": "Would you rather Morning person or Night owl?", "options": ["Morning person", "Night owl"], "tag": "lifestyle"},
    {"text": "Would you rather Jurassic Park or Avatar?", "options": ["Jurassic Park", "Avatar"], "tag": "movie"},
    {"text": "Would you rather Fortnite or Minecraft?", "options": ["Fortnite", "Minecraft"], "tag": "video_game"},
    {"text": "Would you rather Summer or Autumn?", "options": ["Summer", "Autumn"], "tag": "season"},
    {"text": "Would you rather Football or Basketball?", "options": ["Football", "Basketball"], "tag": "sport"},
    {"text": "Would you rather Basketball or Swimming?", "options": ["Basketball", "Swimming"], "tag": "sport"},
    {"text": "Would you rather The Godfather or The Dark Knight?", "options": ["The Godfather", "The Dark Knight"], "tag": "movie"},
    {"text": "Would you rather Handshake or High-five?", "options": ["Handshake", "High-five"], "tag": "greeting"},
    {"text": "Would you rather Hip-hop or Blues?", "options": ["Hip-hop", "Blues"], "tag": "music"},
    {"text": "Would you rather White or Green?", "options": ["White", "Green"], "tag": "color"},
    {"text": "Would you rather Star Wars or The Matrix?", "options": ["Star Wars", "The Matrix"], "tag": "movie"},
    {"text": "Would you rather Call of Duty or Animal Crossing?", "options": ["Call of Duty", "Animal Crossing"], "tag": "video_game"},
    {"text": "Would you rather Jurassic Park or The Matrix?", "options": ["Jurassic Park", "The Matrix"], "tag": "movie"},
    {"text": "Would you rather Red or Yellow?", "options": ["Red", "Yellow"], "tag": "color"},
    {"text": "Would you rather Green or Orange?", "options": ["Green", "Orange"], "tag": "color"},
    {"text": "Would you rather The Godfather or Jurassic Park?", "options": ["The Godfather", "Jurassic Park"], "tag": "movie"},
    {"text": "Would you rather Inception or Avatar?", "options": ["Inception", "Avatar"], "tag": "movie"},
    {"text": "Would you rather Stranger Things or The Simpsons?", "options": ["Stranger Things", "The Simpsons"], "tag": "tv_show"},
    {"text": "Would you rather Train or Bus?", "options": ["Train", "Bus"], "tag": "transport"},
    {"text": "Would you rather Purple or Gray?", "options": ["Purple", "Gray"], "tag": "color"},
    {"text": "Would you rather Black or Brown?", "options": ["Black", "Brown"], "tag": "color"},
    {"text": "Would you rather Blue or Teal?", "options": ["Blue", "Teal"], "tag": "color"},
    {"text": "Would you rather Water or Milk?", "options": ["Water", "Milk"], "tag": "drinks"},
    {"text": "Would you rather Pink or Teal?", "options": ["Pink", "Teal"], "tag": "color"},
    {"text": "Would you rather Eggs or Oatmeal?", "options": ["Eggs", "Oatmeal"], "tag": "breakfast"},
    {"text": "Would you rather Basketball or Cricket?", "options": ["Basketball", "Cricket"], "tag": "sport"},
    {"text": "Would you rather The Dark Knight or Forrest Gump?", "options": ["The Dark Knight", "Forrest Gump"], "tag": "movie"},
    {"text": "Would you rather The Office or Friends?", "options": ["The Office", "Friends"], "tag": "tv_show"},
    {"text": "Would you rather Tennis or Baseball?", "options": ["Tennis", "Baseball"], "tag": "sport"},
    {"text": "Would you rather Tea or Water?", "options": ["Tea", "Water"], "tag": "drinks"},
    {"text": "Would you rather Settlers of Catan or Scrabble?", "options": ["Settlers of Catan", "Scrabble"], "tag": "board_game"},
    {"text": "Would you rather Game of Thrones or Friends?", "options": ["Game of Thrones", "Friends"], "tag": "tv_show"},
    {"text": "Would you rather Golf or Swimming?", "options": ["Golf", "Swimming"], "tag": "sport"},
    {"text": "Would you rather Fish or Rabbit?", "options": ["Fish", "Rabbit"], "tag": "pets"},
    {"text": "Would you rather The Godfather or Titanic?", "options": ["The Godfather", "Titanic"], "tag": "movie"},
    {"text": "Would you rather Minecraft or Overwatch?", "options": ["Minecraft", "Overwatch"], "tag": "video_game"},
    {"text": "Would you rather Coffee or Juice?", "options": ["Coffee", "Juice"], "tag": "drinks"},
    {"text": "Would you rather Scrabble or Risk?", "options": ["Scrabble", "Risk"], "tag": "board_game"},
    {"text": "Would you rather Football or Boxing?", "options": ["Football", "Boxing"], "tag": "sport"},
    {"text": "Would you rather Taylor Swift or Ariana Grande?", "options": ["Taylor Swift", "Ariana Grande"], "tag": "singer"},
    {"text": "Would you rather Settlers of Catan or Clue?", "options": ["Settlers of Catan", "Clue"], "tag": "board_game"},
    {"text": "Would you rather Rugby or Golf?", "options": ["Rugby", "Golf"], "tag": "sport"},
    {"text": "Would you rather Drake or Bruno Mars?", "options": ["Drake", "Bruno Mars"], "tag": "singer"},
    {"text": "Would you rather Salty or Umami?", "options": ["Salty", "Umami"], "tag": "taste"},
    {"text": "Would you rather Taylor Swift or Beyonc\u00e9?", "options": ["Taylor Swift", "Beyonc\u00e9"], "tag": "singer"},
    {"text": "Would you rather The Mandalorian or The Simpsons?", "options": ["The Mandalorian", "The Simpsons"], "tag": "tv_show"},
    {"text": "Would you rather Netflix or Hulu?", "options": ["Netflix", "Hulu"], "tag": "streaming"},
    {"text": "Would you rather Tennis or Swimming?", "options": ["Tennis", "Swimming"], "tag": "sport"},
    {"text": "Would you rather Cricket or Swimming?", "options": ["Cricket", "Swimming"], "tag": "sport"},
    {"text": "Would you rather Billie Eilish or Bruno Mars?", "options": ["Billie Eilish", "Bruno Mars"], "tag": "singer"},
    {"text": "Would you rather Clue or Pandemic?", "options": ["Clue", "Pandemic"], "tag": "board_game"},
    {"text": "Would you rather Blue or Pink?", "options": ["Blue", "Pink"], "tag": "color"},
    {"text": "Would you rather Jazz or Reggae?", "options": ["Jazz", "Reggae"], "tag": "music"},
    {"text": "Would you rather Ed Sheeran or Bruno Mars?", "options": ["Ed Sheeran", "Bruno Mars"], "tag": "singer"},
    {"text": "Would you rather White or Yellow?", "options": ["White", "Yellow"], "tag": "color"},
    {"text": "Would you rather Orange or Pink?", "options": ["Orange", "Pink"], "tag": "color"},
    {"text": "Would you rather Ticket to Ride or Pandemic?", "options": ["Ticket to Ride", "Pandemic"], "tag": "board_game"},
    {"text": "Would you rather Fortnite or Overwatch?", "options": ["Fortnite", "Overwatch"], "tag": "video_game"},
    {"text": "Would you rather Basketball or Tennis?", "options": ["Basketball", "Tennis"], "tag": "sport"},
    {"text": "Would you rather Purple or Pink?", "options": ["Purple", "Pink"], "tag": "color"},
    {"text": "Would you rather Blue or Purple?", "options": ["Blue", "Purple"], "tag": "color"},
    {"text": "Would you rather Minecraft or Call of Duty?", "options": ["Minecraft", "Call of Duty"], "tag": "video_game"},
    {"text": "Would you rather Boat or Bus?", "options": ["Boat", "Bus"], "tag": "transport"},
    {"text": "Would you rather Blues or Folk?", "options": ["Blues", "Folk"], "tag": "music"},
    {"text": "Would you rather Taylor Swift or The Weeknd?", "options": ["Taylor Swift", "The Weeknd"], "tag": "singer"},
    {"text": "Would you rather Avatar or The Dark Knight?", "options": ["Avatar", "The Dark Knight"], "tag": "movie"},
    {"text": "Would you rather Pop or Country?", "options": ["Pop", "Country"], "tag": "music"},
    {"text": "Would you rather Overwatch or Cyberpunk 2077?", "options": ["Overwatch", "Cyberpunk 2077"], "tag": "video_game"},
    {"text": "Would you rather Train or Motorcycle?", "options": ["Train", "Motorcycle"], "tag": "transport"},
    {"text": "Would you rather Train or Scooter?", "options": ["Train", "Scooter"], "tag": "transport"},
    {"text": "Would you rather Friends or Sherlock?", "options": ["Friends", "Sherlock"], "tag": "tv_show"},
    {"text": "Would you rather Scrabble or Carcassonne?", "options": ["Scrabble", "Carcassonne"], "tag": "board_game"},
    {"text": "Would you rather Fortnite or Among Us?", "options": ["Fortnite", "Among Us"], "tag": "video_game"},
    {"text": "Would you rather The Crown or The Simpsons?", "options": ["The Crown", "The Simpsons"], "tag": "tv_show"},
    {"text": "Would you rather Titanic or Jurassic Park?", "options": ["Titanic", "Jurassic Park"], "tag": "movie"},
    {"text": "Would you rather Plane or Motorcycle?", "options": ["Plane", "Motorcycle"], "tag": "transport"},
    {"text": "Would you rather Mountains or Hotel?", "options": ["Mountains", "Hotel"], "tag": "travel"},
    {"text": "Would you rather Handshake or Bow?", "options": ["Handshake", "Bow"], "tag": "greeting"},
    {"text": "Would you rather Bus or Scooter?", "options": ["Bus", "Scooter"], "tag": "transport"},
    {"text": "Would you rather The Office or The Simpsons?", "options": ["The Office", "The Simpsons"], "tag": "tv_show"},
    {"text": "Would you rather Jurassic Park or Pulp Fiction?", "options": ["Jurassic Park", "Pulp Fiction"], "tag": "movie"},
    {"text": "Would you rather Friends or Westworld?", "options": ["Friends", "Westworld"], "tag": "tv_show"},
    {"text": "Would you rather Hand wash or Bath & Shower?", "options": ["Hand wash", "Bath & Shower"], "tag": "hygiene"},
    {"text": "Would you rather Football or Golf?", "options": ["Football", "Golf"], "tag": "sport"},
    {"text": "Would you rather The Office or Westworld?", "options": ["The Office", "Westworld"], "tag": "tv_show"},
    {"text": "Would you rather Pop or Hip-hop?", "options": ["Pop", "Hip-hop"], "tag": "music"},
    {"text": "Would you rather Jurassic Park or Forrest Gump?", "options": ["Jurassic Park", "Forrest Gump"], "tag": "movie"},
    {"text": "Would you rather Country or Blues?", "options": ["Country", "Blues"], "tag": "music"},
    {"text": "Would you rather Overwatch or Elden Ring?", "options": ["Overwatch", "Elden Ring"], "tag": "video_game"},
    {"text": "Would you rather Purple or Brown?", "options": ["Purple", "Brown"], "tag": "color"},
    {"text": "Would you rather Baseball or Rugby?", "options": ["Baseball", "Rugby"], "tag": "sport"},
    {"text": "Would you rather Netflix or Disney+?", "options": ["Netflix", "Disney+"], "tag": "streaming"},
    {"text": "Would you rather Game of Thrones or The Crown?", "options": ["Game of Thrones", "The Crown"], "tag": "tv_show"},
    {"text": "Would you rather City or Hotel?", "options": ["City", "Hotel"], "tag": "travel"},
    {"text": "Would you rather Phone or Tablet?", "options": ["Phone", "Tablet"], "tag": "device"},
    {"text": "Would you rather Online Shopping or In-store Shopping?", "options": ["Online Shopping", "In-store Shopping"], "tag": "shopping"},
    {"text": "Would you rather League of Legends or Overwatch?", "options": ["League of Legends", "Overwatch"], "tag": "video_game"},
    {"text": "Would you rather Billie Eilish or Rihanna?", "options": ["Billie Eilish", "Rihanna"], "tag": "singer"},
    {"text": "Would you rather Black or Red?", "options": ["Black", "Red"], "tag": "color"},
    {"text": "Would you rather Blue or Yellow?", "options": ["Blue", "Yellow"], "tag": "color"},
    {"text": "Would you rather Baseball or Cricket?", "options": ["Baseball", "Cricket"], "tag": "sport"},
    {"text": "Would you rather Carcassonne or Pandemic?", "options": ["Carcassonne", "Pandemic"], "tag": "board_game"},
    {"text": "Would you rather White or Teal?", "options": ["White", "Teal"], "tag": "color"},
    {"text": "Would you rather Pulp Fiction or The Matrix?", "options": ["Pulp Fiction", "The Matrix"], "tag": "movie"},
    {"text": "Would you rather iOS or Mac?", "options": ["iOS", "Mac"], "tag": "technology"},
    {"text": "Would you rather The Mandalorian or The Crown?", "options": ["The Mandalorian", "The Crown"], "tag": "tv_show"},
    {"text": "Would you rather Pancakes or Oatmeal?", "options": ["Pancakes", "Oatmeal"], "tag": "breakfast"},
    {"text": "Would you rather Pop or Electronic?", "options": ["Pop", "Electronic"], "tag": "music"},
    {"text": "Would you rather Hotel or Camping?", "options": ["Hotel", "Camping"], "tag": "travel"},
    {"text": "Would you rather Risk or Carcassonne?", "options": ["Risk", "Carcassonne"], "tag": "board_game"},
    {"text": "Would you rather Books or Movies?", "options": ["Books", "Movies"], "tag": "entertainment"},
    {"text": "Would you rather Breaking Bad or Westworld?", "options": ["Breaking Bad", "Westworld"], "tag": "tv_show"},
    {"text": "Would you rather Chess or Monopoly?", "options": ["Chess", "Monopoly"], "tag": "board_game"},
    {"text": "Would you rather Chrome or Safari?", "options": ["Chrome", "Safari"], "tag": "browser"},
    {"text": "Would you rather Classical or Hip-hop?", "options": ["Classical", "Hip-hop"], "tag": "music"},
    {"text": "Would you rather Yoga or Swimming?", "options": ["Yoga", "Swimming"], "tag": "exercise"},
    {"text": "Would you rather Avatar or The Matrix?", "options": ["Avatar", "The Matrix"], "tag": "movie"},
    {"text": "Would you rather Avatar or Pulp Fiction?", "options": ["Avatar", "Pulp Fiction"], "tag": "movie"},
    {"text": "Would you rather Yellow or Purple?", "options": ["Yellow", "Purple"], "tag": "color"},
    {"text": "Would you rather Beach or Camping?", "options": ["Beach", "Camping"], "tag": "travel"},
    {"text": "Would you rather E-book or Printed Book?", "options": ["E-book", "Printed Book"], "tag": "reading"},
    {"text": "Would you rather Inception or The Dark Knight?", "options": ["Inception", "The Dark Knight"], "tag": "movie"},
    {"text": "Would you rather Stranger Things or Sherlock?", "options": ["Stranger Things", "Sherlock"], "tag": "tv_show"},
    {"text": "Would you rather Purple or Teal?", "options": ["Purple", "Teal"], "tag": "color"},
    {"text": "Would you rather The Godfather or Star Wars?", "options": ["The Godfather", "Star Wars"], "tag": "movie"},
    {"text": "Would you rather White or Purple?", "options": ["White", "Purple"], "tag": "color"},
    {"text": "Would you rather Bronze or Copper?", "options": ["Bronze", "Copper"], "tag": "metal"},
    {"text": "Would you rather Gold or Bronze?", "options": ["Gold", "Bronze"], "tag": "metal"},
    {"text": "Would you rather Monopoly or Carcassonne?", "options": ["Monopoly", "Carcassonne"], "tag": "board_game"},
    {"text": "Would you rather Black or Yellow?", "options": ["Black", "Yellow"], "tag": "color"},
    {"text": "Would you rather Android or Mac?", "options": ["Android", "Mac"], "tag": "technology"},
    {"text": "Would you rather Rugby or Swimming?", "options": ["Rugby", "Swimming"], "tag": "sport"},
    {"text": "Would you rather League of Legends or Animal Crossing?", "options": ["League of Legends", "Animal Crossing"], "tag": "video_game"},
    {"text": "Would you rather Beyonc\u00e9 or Bruno Mars?", "options": ["Beyonc\u00e9", "Bruno Mars"], "tag": "singer"},
    {"text": "Would you rather Call or Text?", "options": ["Call", "Text"], "tag": "communication"},
    {"text": "Would you rather Electronic or Folk?", "options": ["Electronic", "Folk"], "tag": "music"},
    {"text": "Would you rather Sweet or Bitter?", "options": ["Sweet", "Bitter"], "tag": "taste"},
    {"text": "Would you rather Cricket or Golf?", "options": ["Cricket", "Golf"], "tag": "sport"},
    {"text": "Would you rather Inception or The Matrix?", "options": ["Inception", "The Matrix"], "tag": "movie"},
    {"text": "Would you rather Chess or Codenames?", "options": ["Chess", "Codenames"], "tag": "board_game"},
    {"text": "Would you rather Train or Boat?", "options": ["Train", "Boat"], "tag": "transport"},
    {"text": "Would you rather Billie Eilish or The Weeknd?", "options": ["Billie Eilish", "The Weeknd"], "tag": "singer"},
    {"text": "Would you rather Red or Pink?", "options": ["Red", "Pink"], "tag": "color"},
    {"text": "Would you rather Cat or Rabbit?", "options": ["Cat", "Rabbit"], "tag": "pets"},
    {"text": "Would you rather Motorcycle or Scooter?", "options": ["Motorcycle", "Scooter"], "tag": "transport"},
    {"text": "Would you rather Football or Rugby?", "options": ["Football", "Rugby"], "tag": "sport"},
    {"text": "Would you rather PC or Mac?", "options": ["PC", "Mac"], "tag": "technology"},
    {"text": "Would you rather Beyonc\u00e9 or The Weeknd?", "options": ["Beyonc\u00e9", "The Weeknd"], "tag": "singer"},
    {"text": "Would you rather Country or Folk?", "options": ["Country", "Folk"], "tag": "music"},
    {"text": "Would you rather Shower or Bath & Shower?", "options": ["Shower", "Bath & Shower"], "tag": "hygiene"},
    {"text": "Would you rather Clue or Codenames?", "options": ["Clue", "Codenames"], "tag": "board_game"},
    {"text": "Would you rather Drake or Ed Sheeran?", "options": ["Drake", "Ed Sheeran"], "tag": "singer"},
    {"text": "Would you rather Risk or Ticket to Ride?", "options": ["Risk", "Ticket to Ride"], "tag": "board_game"},
    {"text": "Would you rather Mountains or City?", "options": ["Mountains", "City"], "tag": "travel"},
    {"text": "Would you rather Basketball or Hockey?", "options": ["Basketball", "Hockey"], "tag": "sport"},
    {"text": "Would you rather Titanic or Forrest Gump?", "options": ["Titanic", "Forrest Gump"], "tag": "movie"},
    {"text": "Would you rather Salty or Sour?", "options": ["Salty", "Sour"], "tag": "taste"},
    {"text": "Would you rather Green or Teal?", "options": ["Green", "Teal"], "tag": "color"},
    {"text": "Would you rather Inception or Forrest Gump?", "options": ["Inception", "Forrest Gump"], "tag": "movie"},
    {"text": "Would you rather Stranger Things or The Mandalorian?", "options": ["Stranger Things", "The Mandalorian"], "tag": "tv_show"},
    {"text": "Would you rather Red or Blue?", "options": ["Red", "Blue"], "tag": "color"},
    {"text": "Would you rather Hulu or Disney+?", "options": ["Hulu", "Disney+"], "tag": "streaming"},
    {"text": "Would you rather Beyonc\u00e9 or Ariana Grande?", "options": ["Beyonc\u00e9", "Ariana Grande"], "tag": "singer"},
    {"text": "Would you rather Eggs or Cereal?", "options": ["Eggs", "Cereal"], "tag": "breakfast"},
    {"text": "Would you rather Coffee or Milk?", "options": ["Coffee", "Milk"], "tag": "drinks"},
    {"text": "Would you rather Car or Boat?", "options": ["Car", "Boat"], "tag": "transport"},
    {"text": "Would you rather Game of Thrones or Sherlock?", "options": ["Game of Thrones", "Sherlock"], "tag": "tv_show"},
    {"text": "Would you rather Fortnite or Call of Duty?", "options": ["Fortnite", "Call of Duty"], "tag": "video_game"},
    {"text": "Would you rather Hug or Handshake?", "options": ["Hug", "Handshake"], "tag": "greeting"},
    {"text": "Would you rather Orange or Gray?", "options": ["Orange", "Gray"], "tag": "color"},
    {"text": "Would you rather Tablet or Desktop?", "options": ["Tablet", "Desktop"], "tag": "device"},
    {"text": "Would you rather Tea or Juice?", "options": ["Tea", "Juice"], "tag": "drinks"},
    {"text": "Would you rather Pop or Folk?", "options": ["Pop", "Folk"], "tag": "music"},
    {"text": "Would you rather Hockey or Golf?", "options": ["Hockey", "Golf"], "tag": "sport"},
    {"text": "Would you rather Yellow or Pink?", "options": ["Yellow", "Pink"], "tag": "color"},
    {"text": "Would you rather Chess or Clue?", "options": ["Chess", "Clue"], "tag": "board_game"},
    {"text": "Would you rather Bruno Mars or Rihanna?", "options": ["Bruno Mars", "Rihanna"], "tag": "singer"},
    {"text": "Would you rather White or Gray?", "options": ["White", "Gray"], "tag": "color"},
    {"text": "Would you rather Waffles or Eggs?", "options": ["Waffles", "Eggs"], "tag": "breakfast"},
    {"text": "Would you rather Hockey or Boxing?", "options": ["Hockey", "Boxing"], "tag": "sport"},
    {"text": "Would you rather Football or Hockey?", "options": ["Football", "Hockey"], "tag": "sport"},
    {"text": "Would you rather Among Us or Elden Ring?", "options": ["Among Us", "Elden Ring"], "tag": "video_game"},
    {"text": "Would you rather Call of Duty or League of Legends?", "options": ["Call of Duty", "League of Legends"], "tag": "video_game"},
    {"text": "Would you rather Clue or Ticket to Ride?", "options": ["Clue", "Ticket to Ride"], "tag": "board_game"},
    {"text": "Would you rather Hockey or Swimming?", "options": ["Hockey", "Swimming"], "tag": "sport"},
    {"text": "Would you rather Cricket or Rugby?", "options": ["Cricket", "Rugby"], "tag": "sport"},
    {"text": "Would you rather Chess or Scrabble?", "options": ["Chess", "Scrabble"], "tag": "board_game"},
    {"text": "Would you rather Beach or City?", "options": ["Beach", "City"], "tag": "travel"},
    {"text": "Would you rather Dog or Bird?", "options": ["Dog", "Bird"], "tag": "pets"},
    {"text": "Would you rather Juice or Water?", "options": ["Juice", "Water"], "tag": "drinks"},
    {"text": "Would you rather Titanic or Avatar?", "options": ["Titanic", "Avatar"], "tag": "movie"},
    {"text": "Would you rather Jurassic Park or The Dark Knight?", "options": ["Jurassic Park", "The Dark Knight"], "tag": "movie"},
    {"text": "Would you rather Bruno Mars or Adele?", "options": ["Bruno Mars", "Adele"], "tag": "singer"},
    {"text": "Would you rather Breaking Bad or The Crown?", "options": ["Breaking Bad", "The Crown"], "tag": "tv_show"},
    {"text": "Would you rather Blue or Orange?", "options": ["Blue", "Orange"], "tag": "color"},
    {"text": "Would you rather Bitter or Sour?", "options": ["Bitter", "Sour"], "tag": "taste"},
    {"text": "Would you rather Ariana Grande or Adele?", "options": ["Ariana Grande", "Adele"], "tag": "singer"},
    {"text": "Would you rather Monopoly or Clue?", "options": ["Monopoly", "Clue"], "tag": "board_game"},
    {"text": "Would you rather Stranger Things or Westworld?", "options": ["Stranger Things", "Westworld"], "tag": "tv_show"},
    {"text": "Would you rather Fortnite or League of Legends?", "options": ["Fortnite", "League of Legends"], "tag": "video_game"},
    {"text": "Would you rather Blue or Brown?", "options": ["Blue", "Brown"], "tag": "color"},
    {"text": "Would you rather Baseball or Swimming?", "options": ["Baseball", "Swimming"], "tag": "sport"},
    {"text": "Would you rather Bitter or Umami?", "options": ["Bitter", "Umami"], "tag": "taste"},
    {"text": "Would you rather Elden Ring or Valorant?", "options": ["Elden Ring", "Valorant"], "tag": "video_game"},
    {"text": "Would you rather Jazz or Hip-hop?", "options": ["Jazz", "Hip-hop"], "tag": "music"},
    {"text": "Would you rather Avatar or Star Wars?", "options": ["Avatar", "Star Wars"], "tag": "movie"},
    {"text": "Would you rather The Mandalorian or Sherlock?", "options": ["The Mandalorian", "Sherlock"], "tag": "tv_show"},
    {"text": "Would you rather Rock or Hip-hop?", "options": ["Rock", "Hip-hop"], "tag": "music"},
    {"text": "Would you rather Bath or Hand wash?", "options": ["Bath", "Hand wash"], "tag": "hygiene"},
    {"text": "Would you rather Movies or Video Games?", "options": ["Movies", "Video Games"], "tag": "entertainment"},
    {"text": "Would you rather Coffee or Water?", "options": ["Coffee", "Water"], "tag": "drinks"},
    {"text": "Would you rather Swimming or Boxing?", "options": ["Swimming", "Boxing"], "tag": "sport"},
    {"text": "Would you rather Safari or Edge?", "options": ["Safari", "Edge"], "tag": "browser"},
    {"text": "Would you rather Pop or Classical?", "options": ["Pop", "Classical"], "tag": "music"},
    {"text": "Would you rather Pulp Fiction or Star Wars?", "options": ["Pulp Fiction", "Star Wars"], "tag": "movie"},
    {"text": "Would you rather Plane or Scooter?", "options": ["Plane", "Scooter"], "tag": "transport"},
    {"text": "Would you rather Pancakes or Eggs?", "options": ["Pancakes", "Eggs"], "tag": "breakfast"},
    {"text": "Would you rather Titanic or Star Wars?", "options": ["Titanic", "Star Wars"], "tag": "movie"},
    {"text": "Would you rather Game of Thrones or Westworld?", "options": ["Game of Thrones", "Westworld"], "tag": "tv_show"},
    {"text": "Would you rather YouTube or Hulu?", "options": ["YouTube", "Hulu"], "tag": "streaming"},
    {"text": "Would you rather Basketball or Boxing?", "options": ["Basketball", "Boxing"], "tag": "sport"},
    {"text": "Would you rather Fortnite or Animal Crossing?", "options": ["Fortnite", "Animal Crossing"], "tag": "video_game"},
    {"text": "Would you rather Game of Thrones or Stranger Things?", "options": ["Game of Thrones", "Stranger Things"], "tag": "tv_show"},
    {"text": "Would you rather Rock or Country?", "options": ["Rock", "Country"], "tag": "music"},
    {"text": "Would you rather Hug or High-five?", "options": ["Hug", "High-five"], "tag": "greeting"},
    {"text": "Would you rather Call of Duty or Valorant?", "options": ["Call of Duty", "Valorant"], "tag": "video_game"},
    {"text": "Would you rather iOS or PC?", "options": ["iOS", "PC"], "tag": "technology"},
    {"text": "Would you rather Classical or Electronic?", "options": ["Classical", "Electronic"], "tag": "music"},
    {"text": "Would you rather Chess or Ticket to Ride?", "options": ["Chess", "Ticket to Ride"], "tag": "board_game"},
    {"text": "Would you rather Jazz or Country?", "options": ["Jazz", "Country"], "tag": "music"},
    {"text": "Would you rather Taylor Swift or Ed Sheeran?", "options": ["Taylor Swift", "Ed Sheeran"], "tag": "singer"},
    {"text": "Would you rather White or Red?", "options": ["White", "Red"], "tag": "color"},
    {"text": "Would you rather Board Games or Video Games?", "options": ["Board Games", "Video Games"], "tag": "entertainment"},
    {"text": "Would you rather Swimming or Cycling?", "options": ["Swimming", "Cycling"], "tag": "exercise"},
    {"text": "Would you rather Car or Plane?", "options": ["Car", "Plane"], "tag": "transport"},
    {"text": "Would you rather Call or Email?", "options": ["Call", "Email"], "tag": "communication"},
    {"text": "Would you rather Ariana Grande or Rihanna?", "options": ["Ariana Grande", "Rihanna"], "tag": "singer"},
    {"text": "Would you rather Black or Purple?", "options": ["Black", "Purple"], "tag": "color"},
    {"text": "Would you rather Pilates or Swimming?", "options": ["Pilates", "Swimming"], "tag": "exercise"},
    {"text": "Would you rather Cereal or Oatmeal?", "options": ["Cereal", "Oatmeal"], "tag": "breakfast"},
    {"text": "Would you rather League of Legends or Valorant?", "options": ["League of Legends", "Valorant"], "tag": "video_game"},
    {"text": "Would you rather Westworld or Sherlock?", "options": ["Westworld", "Sherlock"], "tag": "tv_show"},
    {"text": "Would you rather Ariana Grande or Billie Eilish?", "options": ["Ariana Grande", "Billie Eilish"], "tag": "singer"},
    {"text": "Would you rather Tennis or Rugby?", "options": ["Tennis", "Rugby"], "tag": "sport"},
    {"text": "Would you rather Orange or Brown?", "options": ["Orange", "Brown"], "tag": "color"},
    {"text": "Would you rather Football or Cricket?", "options": ["Football", "Cricket"], "tag": "sport"},
    {"text": "Would you rather Monopoly or Codenames?", "options": ["Monopoly", "Codenames"], "tag": "board_game"},
    {"text": "Would you rather Soda or Milk?", "options": ["Soda", "Milk"], "tag": "drinks"},
    {"text": "Would you rather Football or Baseball?", "options": ["Football", "Baseball"], "tag": "sport"},
    {"text": "Would you rather Breaking Bad or The Simpsons?", "options": ["Breaking Bad", "The Simpsons"], "tag": "tv_show"},
    { "text": "Sweet or savory breakfast?", "options": ["Sweet", "Savory"], "tag": "food" },
    { "text": "Morning person or night owl?", "options": ["Morning", "Night"], "tag": "lifestyle" },
    { "text": "Beach or mountains?", "options": ["Beach", "Mountains"], "tag": "travel" },
    { "text": "Would you rather summer or winter?", "options": ["Summer", "Winter"], "tag": "season" },
    { "text": "Would you rather pizza or burgers?", "options": ["Pizza", "Burgers"], "tag": "food" },
    { "text": "Would you rather books or movies?", "options": ["Books", "Movies"], "tag": "entertainment" },
    { "text": "Would you rather train or plane?", "options": ["Train", "Plane"], "tag": "travel" },
    { "text": "Would you rather car or bicycle?", "options": ["Car", "Bicycle"], "tag": "transport" },
    { "text": "Would you rather android or ios?", "options": ["Android", "iOS"], "tag": "technology" },
    { "text": "Would you rather pc or mac?", "options": ["PC", "Mac"], "tag": "technology" },
    { "text": "Would you rather chrome or firefox?", "options": ["Chrome", "Firefox"], "tag": "browser" },
    { "text": "Would you rather call or text?", "options": ["Call", "Text"], "tag": "communication" },
    { "text": "Would you rather hug or handshake?", "options": ["Hug", "Handshake"], "tag": "greeting" },
    { "text": "Would you rather board games or video games?", "options": ["Board Games", "Video Games"], "tag": "games" },
    { "text": "Would you rather science or arts?", "options": ["Science", "Arts"], "tag": "subject" },
    { "text": "Would you rather sneakers or sandals?", "options": ["Sneakers", "Sandals"], "tag": "footwear" },
    { "text": "Would you rather black or white?", "options": ["Black", "White"], "tag": "color" },
    { "text": "Would you rather netflix or youtube?", "options": ["Netflix", "YouTube"], "tag": "streaming" },
    { "text": "Would you rather stairs or elevator?", "options": ["Stairs", "Elevator"], "tag": "facility" },
    { "text": "Would you rather bath or shower?", "options": ["Bath", "Shower"], "tag": "hygiene" },
    { "text": "Would you rather pancakes or waffles?", "options": ["Pancakes", "Waffles"], "tag": "breakfast" },
    { "text": "Would you rather tea or juice?", "options": ["Tea", "Juice"], "tag": "drink" },
    { "text": "Would you rather salty or sweet?", "options": ["Salty", "Sweet"], "tag": "taste" },
    { "text": "Would you rather gold or silver?", "options": ["Gold", "Silver"], "tag": "metal" },
    { "text": "Would you rather comedy or drama?", "options": ["Comedy", "Drama"], "tag": "movie" },
    { "text": "Would you rather football or basketball?", "options": ["Football", "Basketball"], "tag": "sports" },
    { "text": "Would you rather pen or pencil?", "options": ["Pen", "Pencil"], "tag": "stationery" },
    { "text": "Would you rather chocolate or vanilla?", "options": ["Chocolate", "Vanilla"], "tag": "flavor" },
    { "text": "Would you rather pool or beach?", "options": ["Pool", "Beach"], "tag": "location" },
    { "text": "Would you rather phone or laptop?", "options": ["Phone", "Laptop"], "tag": "device" },
    { "text": "Would you rather twitter or instagram?", "options": ["Twitter", "Instagram"], "tag": "social" },
    { "text": "Would you rather morning gym or evening gym?", "options": ["Morning Gym", "Evening Gym"], "tag": "exercise" },
    { "text": "Would you rather yoga or pilates?", "options": ["Yoga", "Pilates"], "tag": "exercise" },
    { "text": "Would you rather city or countryside?", "options": ["City", "Countryside"], "tag": "travel" },
    { "text": "Would you rather camping or hotel?", "options": ["Camping", "Hotel"], "tag": "accommodation" },
    { "text": "Would you rather museum or zoo?", "options": ["Museum", "Zoo"], "tag": "place" },
    { "text": "Would you rather sushi or tacos?", "options": ["Sushi", "Tacos"], "tag": "food" },
    { "text": "Would you rather hotdog or burger?", "options": ["Hotdog", "Burger"], "tag": "food" },
    { "text": "Would you rather rain or snow?", "options": ["Rain", "Snow"], "tag": "weather" },
    { "text": "Would you rather sunrise or sunset?", "options": ["Sunrise", "Sunset"], "tag": "time" },
    { "text": "Would you rather rock or pop?", "options": ["Rock", "Pop"], "tag": "music" },
    { "text": "Would you rather classical or hip-hop?", "options": ["Classical", "Hip-hop"], "tag": "music" },
    { "text": "Would you rather e-book or printed book?", "options": ["E-book", "Printed Book"], "tag": "reading" },
    { "text": "Would you rather online shopping or in-store shopping?", "options": ["Online Shopping", "In-store Shopping"], "tag": "shopping" }
    
]

# Assign unique IDs to each question
for i, q in enumerate(QUIZ_QUESTIONS):
    q['id'] = i + 1

# Get or create an active batch for a user pair
def get_or_create_batch(user_id, partner_id):
    # Sort IDs to ensure consistent pair identification
    pair = sorted([str(user_id), str(partner_id)])
    
    # Check for existing active batch
    batch = mongo.db.quiz_batches.find_one({
        'user1_id': pair[0],
        'user2_id': pair[1],
        'completed': False,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    
    if batch:
        return batch
    
    # Create a new batch with 5 random questions
    questions = random.sample(QUIZ_QUESTIONS, 5)
    
    batch = {
        'user1_id': pair[0],
        'user2_id': pair[1],
        'questions': questions,
        'created_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=7),
        'completed': False,
        'current_index': 0
    }
    
    result = mongo.db.quiz_batches.insert_one(batch)
    # Retrieve the inserted document to return
    return mongo.db.quiz_batches.find_one({'_id': result.inserted_id})

# Get compatibility score
@quiz_bp.route('/score', methods=['GET'])
@jwt_required()
def get_score():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'score': 0, 'message': 'No partner connected'}), 200
        
        # Get score from database
        pair = sorted([str(uid), str(partner_id)])
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        
        # Count total responses and matches
        total_questions = mongo.db.quiz_responses.count_documents({
            'user_id': uid
        })
        
        # Count matches
        matches = 0
        user_responses = list(mongo.db.quiz_responses.find({'user_id': uid}))
        
        for resp in user_responses:
            partner_resp = mongo.db.quiz_responses.find_one({
                'user_id': partner_id,
                'question_id': resp['question_id']
            })
            
            if partner_resp and partner_resp['answer'] == resp['answer']:
                matches += 1
        
        # Calculate match percentage
        match_percent = 0
        if total_questions > 0:
            partner_responses = mongo.db.quiz_responses.count_documents({
                'user_id': partner_id,
                'question_id': {'$in': [r['question_id'] for r in user_responses]}
            })
            
            if partner_responses > 0:
                match_percent = round((matches / partner_responses) * 100)
        
        return jsonify({
            'score': score_doc['score'] if score_doc else 0,
            'total_answered': total_questions,
            'matches': matches,
            'match_percent': match_percent
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error fetching score: %s", str(e))
        return jsonify({'score': 0, 'error': str(e)}), 200

# Status endpoint - get current quiz status
@quiz_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({
                'has_partner': False,
                'message': 'No partner connected'
            }), 200
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        # Check for questions answered by partner but not user
        user_answered = list(mongo.db.quiz_responses.distinct('question_id', {
            'user_id': uid
        }))
        
        partner_answered = list(mongo.db.quiz_responses.distinct('question_id', {
            'user_id': partner_id
        }))
        
        pending_questions = [q for q in partner_answered if q not in user_answered]
        
        # Get compatibility score
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        
        return jsonify({
            'has_partner': True,
            'partner_name': user.get('partner_name', 'Partner'),
            'current_score': score_doc['score'] if score_doc else 0,
            'has_active_batch': batch is not None,
            'pending_questions': len(pending_questions),
            'batch_info': {
                'id': str(batch['_id']) if batch else None,
                'progress': f"{batch['current_index']}/{len(batch['questions'])}" if batch else "0/0",
                'completed': batch['completed'] if batch else False
            } if batch else None
        }), 200
    except Exception as e:
        current_app.logger.exception("Error fetching status: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Batch endpoints
@quiz_bp.route('/batch', methods=['GET'])
@jwt_required()
def get_batch():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get or create batch
        batch = get_or_create_batch(uid, partner_id)
        
        return jsonify({
            'batch_id': str(batch['_id']),
            'total_questions': len(batch['questions']),
            'current_index': batch['current_index'],
            'completed': batch['completed'],
            'expires_at': batch['expires_at'].isoformat()
        }), 200
    except Exception as e:
        current_app.logger.exception("Error getting batch: %s", str(e))
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/batch/new', methods=['POST'])
@jwt_required()
def create_new_batch():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Mark existing batches as completed
        pair = sorted([str(uid), str(partner_id)])
        mongo.db.quiz_batches.update_many(
            {'user1_id': pair[0], 'user2_id': pair[1], 'completed': False},
            {'$set': {'completed': True}}
        )
        
        # Create new batch
        batch = get_or_create_batch(uid, partner_id)
        
        return jsonify({
            'message': 'New batch created',
            'batch_id': str(batch['_id']),
            'total_questions': len(batch['questions'])
        }), 200
    except Exception as e:
        current_app.logger.exception("Error creating batch: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Get current question
@quiz_bp.route('/question', methods=['GET'])
@jwt_required()
def get_question():
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get active batch
        batch = get_or_create_batch(uid, partner_id)
        
        # Check if batch is complete
        if batch['current_index'] >= len(batch['questions']):
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$set': {'completed': True}}
            )
            return jsonify({'message': 'Batch completed', 'completed': True}), 200
        
        # Get current question
        current_q = batch['questions'][batch['current_index']]
        
        # Check if user has already answered this question
        existing_answer = mongo.db.quiz_responses.find_one({
            'user_id': uid,
            'question_id': current_q['id']
        })
        
        if existing_answer:
            # Move to next question if already answered
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$inc': {'current_index': 1}}
            )
            # Recursive call to get next question
            return get_question()
        
        # Return the current question
        return jsonify({
            'id': current_q['id'],
            'question': current_q['text'],
            'options': current_q['options'],
            'batch_progress': {
                'current': batch['current_index'] + 1,
                'total': len(batch['questions'])
            }
        }), 200
    except Exception as e:
        current_app.logger.exception("Error getting question: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Submit answer
@quiz_bp.route('/answer', methods=['POST'])
@jwt_required()
def submit_answer():
    uid = get_jwt_identity()
    data = request.json or {}
    
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if not question_id or answer is None:
        return jsonify({'message': 'question_id and answer required'}), 400
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        if not batch:
            return jsonify({'error': 'No active question batch'}), 400
        
        # Save response
        mongo.db.quiz_responses.insert_one({
            'user_id': uid,
            'question_id': question_id,
            'answer': answer,
            'created_at': datetime.utcnow(),
            'batch_id': str(batch['_id'])
        })
        
        # Check if partner has answered
        partner_resp = mongo.db.quiz_responses.find_one({
            'user_id': partner_id,
            'question_id': question_id
        })
        
        # Initialize response data
        response_data = {
            'message': 'Answer submitted',
            'waiting_for_partner': True,
            'delta': 0,
            'is_match': False,
            'new_score': None,
            'batch_complete': False
        }
        
        # If partner has answered this question
        if partner_resp:
            is_match = partner_resp['answer'] == answer
            delta = 5 if is_match else -2
            
            # Update response data
            response_data['waiting_for_partner'] = False
            response_data['is_match'] = is_match
            response_data['delta'] = delta
            
            # Update compatibility score
            score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
            
            if score_doc:
                new_score = max(0, score_doc['score'] + delta)
                mongo.db.quiz_scores.update_one(
                    {'user1_id': pair[0], 'user2_id': pair[1]},
                    {'$set': {'score': new_score}}
                )
            else:
                new_score = max(0, delta)
                mongo.db.quiz_scores.insert_one({
                    'user1_id': pair[0],
                    'user2_id': pair[1],
                    'score': new_score
                })
            
            response_data['new_score'] = new_score
            
            # Move to next question in batch
            mongo.db.quiz_batches.update_one(
                {'_id': batch['_id']},
                {'$inc': {'current_index': 1}}
            )
            
            # Check if batch is complete
            updated_batch = mongo.db.quiz_batches.find_one({'_id': batch['_id']})
            if updated_batch['current_index'] >= len(batch['questions']):
                mongo.db.quiz_batches.update_one(
                    {'_id': batch['_id']},
                    {'$set': {'completed': True}}
                )
                response_data['batch_complete'] = True
        
        return jsonify(response_data), 200
    except Exception as e:
        current_app.logger.exception("Error submitting answer: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Get batch results (for review at end of batch)
@quiz_bp.route('/batch/<batch_id>/results', methods=['GET'])
@jwt_required()
def get_batch_results(batch_id):
    uid = get_jwt_identity()
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Get the batch
        batch = mongo.db.quiz_batches.find_one({'_id': ObjectId(batch_id)})
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        # Get answers for this batch
        user_responses = list(mongo.db.quiz_responses.find({
            'user_id': uid,
            'batch_id': batch_id
        }))
        
        partner_responses = list(mongo.db.quiz_responses.find({
            'user_id': partner_id,
            'batch_id': batch_id
        }))
        
        # Format results
        results = []
        
        for q in batch['questions']:
            user_answer = next((r['answer'] for r in user_responses if r['question_id'] == q['id']), None)
            partner_answer = next((r['answer'] for r in partner_responses if r['question_id'] == q['id']), None)
            
            if user_answer is not None and partner_answer is not None:
                results.append({
                    'question': q['text'],
                    'your_answer': user_answer,
                    'partner_answer': partner_answer,
                    'match': user_answer == partner_answer
                })
        
        return jsonify({'questions': results}), 200
    except Exception as e:
        current_app.logger.exception("Error getting batch results: %s", str(e))
        return jsonify({'error': str(e)}), 500

# Legacy endpoints to maintain backward compatibility
@quiz_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_by_id(question_id):
    # Return a random question for compatibility
    q = random.choice(QUIZ_QUESTIONS)
    return jsonify({
        'id': question_id,
        'question': q['text'],
        'options': q['options']
    }), 200

# Add this endpoint to your quiz.py file

@quiz_bp.route('/check-partner-response', methods=['GET'])
@jwt_required()
def check_partner_response():
    uid = get_jwt_identity()
    question_id = request.args.get('question_id')
    
    if not question_id:
        return jsonify({'error': 'question_id is required'}), 400
    
    try:
        # Get user info
        user = mongo.db.users.find_one({'_id': ObjectId(uid)})
        partner_id = user.get('partner_id', '')
        
        if not partner_id:
            return jsonify({'error': 'No partner connected'}), 400
        
        # Check if partner has answered this question
        partner_resp = mongo.db.quiz_responses.find_one({
            'user_id': partner_id,
            'question_id': int(question_id)
        })
        
        if not partner_resp:
            # Partner hasn't answered yet
            return jsonify({
                'has_answered': False
            }), 200
        
        # Partner has answered, check if user has answered too
        user_resp = mongo.db.quiz_responses.find_one({
            'user_id': uid,
            'question_id': int(question_id)
        })
        
        if not user_resp:
            # User hasn't answered yet (unusual case)
            return jsonify({
                'has_answered': False
            }), 200
        
        # Both have answered, check for match
        is_match = partner_resp['answer'] == user_resp['answer']
        delta = 5 if is_match else -2
        
        # Get active batch
        pair = sorted([str(uid), str(partner_id)])
        batch = mongo.db.quiz_batches.find_one({
            'user1_id': pair[0],
            'user2_id': pair[1],
            'completed': False
        })
        
        # Get or update score
        score_doc = mongo.db.quiz_scores.find_one({'user1_id': pair[0], 'user2_id': pair[1]})
        new_score = None
        
        if score_doc:
            new_score = score_doc['score']
        
        # Check if batch is complete
        batch_complete = False
        if batch:
            current_index = batch.get('current_index', 0)
            total_questions = len(batch.get('questions', []))
            batch_complete = current_index >= total_questions
        
        return jsonify({
            'has_answered': True,
            'is_match': is_match,
            'delta': delta,
            'new_score': new_score,
            'batch_complete': batch_complete
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error checking partner response: %s", str(e))
        return jsonify({'error': str(e)}), 500
