"""Default hero image captions for initiative home pages."""

INITIATIVE_CAPTIONS = {
    'ankurayan': {
        'en': '"A festival of light and delight for children"',
        'or': '"ଶିଶୁମାନଙ୍କ ପାଇଁ ଆଲୋକ ଓ ଆନନ୍ଦର ଏକ ଉତ୍ସବ"',
    },
    'anandakendra': {
        'en': '"Man making initiative of Bandhu"',
        'or': '"ଏକ ପ୍ରେରେଣାଶୀଳ ନୂଆପିଢୀର ନିର୍ମାଣେ"',
    },
    'ashram': {
        'en': '"A home of care and dignity helps every heart feel safe."',
        'or': '"ସ୍ନେହ ଓ ସମ୍ମାନର ଘରେ ପ୍ରତ୍ୟେକ ହୃଦୟ ନିରାପଦ ଅନୁଭବ କରେ।"',
    },
    'charitywork': {
        'en': '"Service grows brighter when many hands and hearts come together."',
        'or': '"ଅନେକ ହାତ ଓ ହୃଦୟ ଏକାତ୍ମ ହେଲେ ସେବା ଅଧିକ ଉଜ୍ଜ୍ୱଳ ହୁଏ।"',
    },
    'patriotism': {
        'en': '"Patriotism grows through action and learning."',
        'or': '"କାର୍ଯ୍ୟ ଓ ଶିକ୍ଷା ମାଧ୍ୟମରେ ଦେଶପ୍ରେମ ବୃଦ୍ଧି ପାଏ।"',
    },
    'sevavrata': {
        'en': '"Service is the finest tribute to our land."',
        'or': '"ସେବା ହେଉଛି ମାଟିପାଇଁ ସର୍ବୋତ୍ତମ ଶ୍ରଦ୍ଧାଞ୍ଜଲି।"',
    },
    'prasantaraktadan': {
        'en': '"Every drop donated is a gift of life."',
        'or': '"ପ୍ରତ୍ୟେକ ରକ୍ତଦାନ ଜୀବନର ଉପହାର।"',
    },
}


def apply_initiative_captions(homepage, app_label):
    """Set default captions when fields are empty."""
    captions = INITIATIVE_CAPTIONS.get(app_label, {})
    changed = False
    if captions.get('en') and not (getattr(homepage, 'image_caption_en', None) or '').strip():
        homepage.image_caption_en = captions['en']
        changed = True
    if captions.get('or') and not (getattr(homepage, 'image_caption_or', None) or '').strip():
        homepage.image_caption_or = captions['or']
        changed = True
    return changed
