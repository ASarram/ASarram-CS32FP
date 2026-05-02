SONG/DANCE STYLE DETECTOR

Analyzes an audio file and identifies the ballroom dance that it mathces best (cha cha, samba, rumba, paso doble, or jive - but can be tailored to user's preference) using audio feature extraction and a reference database created from training samples 



--- Function of Code --- 
1. Downloads audio file from YouTube URL 
2. Extracts following audio features: BPM, energy, beat strength, spectral brightness, beat regularity, and spectral rolloff
3. Extracts features from multive segments of the song and averages them for more representative result 
4. Compares extracted features against reference database of known dance style profiles
5. Outputs best matching dance style with confidence score and explanation by feature



--- Project files --- 
* main.py -> entry point for detector, that handles YouTube download of input file, and calls matching
* matching.py -> contains scoring and explanation logic
* helpers.py -> contains helper functions (feature extraction)
* build_database.py -> builds reference database from training audiofiles
* collect_data.py -> helper script for database creation (handles downloads of training audio from YouTube)



--- Setup Information --- 

Part 1: Initial Setup 
  1. Required installations: librosa, numpy and yt-dlp
  2. Set up cookies.txt (for YouTube downloads)
     a. Install the "Get cookies.txt LOCALLY" extension for Chrome
     b. Log into YouTube in browser
     c. Click on extension and export; save file locally within project as "cookies.txt"
  
Part 2: DataBase Setup 
  1. Populate the data/ folders with training audio. Can do this either by adding audio manually or using   collect_data.py
  2. Run build_database.py to create the database -> profile for each dance style will be saved to database.json

*NOTE: code ideally should be run in local IDE for correct functioning of cookie authentication*

--- External Contributors --- 

Key Libraries: 
* librosa -> for audio analysis and feature extraction
* yt-dlp -> for YouTube audio downloading
* numpy -> for numerical operations


Additional Resources 
Google search and online Python support websites were used as needed 
Generative AI (specifically Claude) was used in the following ways, which are explicitly flagged and explained via script commments: 
* download_from_youtube() in main.py: AI assistance was used to write the yt-dlp command structure and --print after_move: filepath flag to capture output path
* Confidence scoring in matching.py: idea of normalization of weights and implementation of exponential decay scoring was written with AI assistance
* z-score capping in matching.py: idea of capping z-score to avoid having single outliers dominate results 


  



