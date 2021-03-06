from flask import Flask, request, redirect
import twilio.twiml

authorized_users = ["+12064273590"] # matt's # as first auth user
locked_state = True # locked by default

app = Flask(__name__)

def parse_request(txt, sender):
  global authorized_users
  global locked_state

  if "unlock" in txt.lower():
    locked_state = False
    return "Lock will unlock."
  elif "add" in txt.lower() or "remove" in txt.lower():
    to_mod = txt.split()[1]
    if sender != authorized_users[0]:
      return "Only first authorized user can add or remove other users." # basic security
    if "+1" in to_mod and len(to_mod) == 12: # should be more robust
      if "add" in txt.lower():
        authorized_users.append(to_mod)
        return "User " + to_mod + " added to authorized users."
      elif "remove" in txt.lower() and to_mod != authorized_users[0]: # don't wreak havoc
        authorized_users.remove(to_mod)
        return "User " + to_mod + " removed from authorized users."
    else:
      return to_mod + " not recognized (valid example: +12065551234)."
  return "Unrecognized command!"

@app.route("/", methods=['GET', 'POST'])
def handle_sms():
    global authorized_users

    txt = request.values.get('Body', None)
    sender = request.values.get('From', None)

    resp = twilio.twiml.Response()
    if txt and sender in authorized_users:
      resp.sms(parse_request(txt, sender))
    elif txt:
      resp.sms("You're not an authorized user!")
    else:
      resp.sms("No message content received...")

    return str(resp)

@app.route("/state", methods=['GET', 'POST'])
def handle_state_check():
  global locked_state

  is_locked = locked_state
  locked_state = True # lock after checking
  return "Unlocked" if not is_locked else "Locked"

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=6288, debug=True)