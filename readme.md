### Project Goal
Build a ML model to classify personal email data as either spam or not spam.

### Program functions
* Load email data
  * gmail data via gmail api
  * proton data via proton cmd tool (json file loading)
* Analyze data to find patterns
* Preprocess and train model
* Classify new email data as spam or non spam

### Definitions
**Spam email definition:** An email which is unsolicited and often times is an advertisement or promotional type email.

**Non spam email definition:** An email that I/the email user should see and not automatically put in a spam folder.
Non spam emails may be often deleted without being read, but we'd rather this happen than the user not see a email that they should have seen.

**Examples:**  
1. Email subject: "[2]2 messages in conversationNew Badge Received" 
Sender "kaggle-noreply@google.com".
    - Classified as non spam
    - Although I don't care much about what badges I've earned, this email is informative about something that happened on my Kaggle account.
      I would rather see it than not.
2. Email subject: "Steve G and 4 others gave you kudos!" sender "mail@update.strava.com"
    - Classified as non spam
    - Although I often delete these emails right away I'd still rather see them than not.
3. Email subject: "Spring into Earth Day Savings!" sender: "noreply@marketing.xcelenergy.com"
    - Classified as spam
    - This is promotional content, not something I care to see in my inbox so it is classified as spam.

### Training notes
- TFIDF takes in a pandas series not a 2d dataframe
- Using LinearSVC model (3 folds cross val)
  - Using 3 folds for cross validation
  - One hot encoder for all features = 91.65%
  - One hot encoder for sender local and domain and TFIDF for subject = 94.03%
  - Lower casing features, no noticeable accuracy change 
  - Confusion matrix as follows:  
  [[510  90]
  [ 53 881]]
- Using LogisticRegression model
  - Using 3 folds for cross validation
  - One hot encoder for all features = 90.6%
  - One hot encoder for sender local and domain and TFIDF for subject = 93.75%
- Both models overfit initially
  - May need more training data and some regularization
  - ~8% gap between training predictions and validation predictions 
### TODO
- Regularize model to prevent overfitting (see training analysis graph)
- Adjust for higher precision
- Gather more post training analysis data
    - F1 score, precision, recall
- Hook up to proton bridge to read email data
  - Utilize imaplib package
- Use proton bridge/IMAP protocol to classify new incoming emails and move to folder
  