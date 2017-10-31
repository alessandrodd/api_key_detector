import sys

import rstr

# viglink = instagram client id = TMDB (IMDB) = twilio token = spotify secret = openweather api key
# = facebook app secret
# redmine token = githubseret
# guid lowercase = heroku
regs = {"amazonaws": "[0-9a-zA-Z/+]{40}", "bitly": "R_[0-9a-f]{32}", "facebookappsecret": "[0-9a-f]{32}",
        "flickr": "[0-9a-f]{16}", "guidupper": "[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
        "foursquare": "[0-9A-Z]{48}", "linkedin": "[0-9a-zA-Z]{16}", "twitter": "[0-9a-zA-Z]{35,44}",
        "mailgun": "key-[0-9a-f]{32}", "sendgrid": "SG[.][0-9a-zA-Z-_]{22}[.][0-9a-zA-Z-_]{37}-[0-9a-zA-Z]{5}",
        "googleauthtoken": "[0-9a-zA-Z-_/]{70}[.]", "mailchimp": "[0-9a-f]{32}-us[0-9]{1,2}",
        "githubkey": "[0-9a-f]{20}",
        "githubsecret": "[0-9a-f]{40}", "stripelivekey": "sk_live_[0-9a-zA-Z]{24}",
        "googlemaps": "AIzaSy[0-9a-zA-Z-_]{33}", "slacktoken": "xoxb-[0-9]{11}-[0-9a-zA-Z]{24}",
        "beepbooptoken": "[0-9a-f]{32}-[0-9]{9}", "mashapekey": "[0-9a-zA-Z]{50}", "gitlabtoken": "[0-9a-zA-Z]{20}",
        "herokuapikey": "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "base91": "[\\x21-\\x26\\x28-\\x2C\\x2E-\\x5B\\x5D-\\x7E]{16,40}"}


def main(argv):
    if len(argv) != 2 and len(argv) != 3:
        print("Usage: python {0} number_of_keys [single_file_path]".format(argv[0]))
        return
    elif len(argv) == 3:
        with open(argv[2], 'w') as f:
            for r in regs.items():
                for i in range(0, int(argv[1])):
                    key = rstr.xeger(r[1])
                    f.write(key)
                    if i != (int(argv[1]) - 1) or r != list(regs.items())[-1]:
                        f.write("\n")
                    print(key)
    else:
        for r in regs.items():
            with open("gen_" + r[0] + ".txt", 'w') as f:
                for i in range(0, int(argv[1])):
                    key = rstr.xeger(r[1])
                    f.write(key)
                    if i != (int(argv[1]) - 1):
                        f.write("\n")
                    print(key)


if __name__ == '__main__':
    main(sys.argv)
