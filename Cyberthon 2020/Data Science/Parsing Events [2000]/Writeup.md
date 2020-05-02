# Task
We found a network event log that the attackers forgot to delete. The logs are in a strange format though. We have a few questions that we want to find the answers to - can you help us?\
Note: Your answers should be a text file with each answer on a separate line. Messages should have the outer " removed. Leave blank lines for questions that you are not answering.

**Example:**

Logs:
> Bob sent "Hi!" to Alice at 4.30pm.\
> At 3.50am, "Welcome!" was sent to Charlie by Alice.

Questions:
> What did Charlie send to Alice at 3.50am?\
> Who sent "Hi!"?

Answers:
>Welcome!\
>Bob

Answer have the format of: a single column CSV file with header `answer`

**Files**: [logs.txt](logs.txt), [questions.txt](questions.txt)

# Method
Looking at the logs, each line has 4 pieces of information:
 - a message, enclosed in double quotes `"`,
 - a date/time, in the format `YYYY-MM-DD HH:MM:SS` (please tell me you know which `M`s are month and minute),
 - 2 users, a sender and recipient, both formatted as IPv6 addresses: 8 blocks of up to 4 hex digits each, delimited by colons `:`.

Searching for these patterns in strings are _precisely_ what regular expressions were built for. They give us a shortcut to process and extract the required substrings efficiently, yet also with clear and concise code.

 - Messages can be matched with `"[^"]+"`,
 - Date/time can be matched with `\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}`, and
 - IPv6 addresses can be matched with `[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}`.

The only issue is with differentiating between sender and recipient in each. For this, notice that each user is surrounded by some text indicating (grammatically) whether the user being referred to is a sender or recipient. In these logs, the sender is always either in the format `<user> sent` or `sent ... by <user>`, and the recipient is always either in the format `<user> was sent` or `sent ... to <user>`. This way, we can simply extend our regexes to include this surrounding text.

With this, we process the logs into arrays of messages, date/times, senders, and recipients:
```py
msgs, dts, sndrs, rcpnts = [], [], [], []
msg_re = re.compile(r'"[^"]+"')
dt_re = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')
sndr_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} sent | by [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')
rcpnt_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} was sent | to [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')

for line in logs: # 100,000
	msgs.append(msg_re.search(line).group(0))
	dts.append(dt_re.search(line).group(0))
	sndr, rcpnt = sndr_re.search(line).group(0), rcpnt_re.search(line).group(0)
	sndrs.append(sndr[4:] if sndr[0]==' ' else sndr[:-6]) # just user address, chop off surrounding excess
	rcpnts.append(rcpnt[4:] if rcpnt[0]==' ' else rcpnt[:-10]) # just user address, chop off surrounding excess
```

Looking at the questions now, each query gives 1 to 3 of these pieces of information, and requests for 1 of the missing ones. Every question starts with `Who sent <message>`, `Who did <user> send <message>`, `What did <user> send at <date/time>`, or `Who did <user> receive a message from at <date/time>`. There is usually more information following these starting points, but the first 1 or 2 pieces of information is sufficient for us to uniquely determine what we need.\
Again, using regexes makes this so much more convenient and readable (than say, a bunch of nested if's and substring checks and other string manipulation).

```py
usr_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')
t1_re = re.compile(r'Who sent "[^"]+"')
t2_re = re.compile(r'Who did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} send "[^"]+"')
t3_re = re.compile(r'What did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} send at \d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')
t4_re = re.compile(r'Who did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} receive a message from at \d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')
```

Now for each question, we simply iteratively loop through the corresponding processed arrays, and select those that match the information in the questions. This requires at most `5000 * 1e5 == 5e8` operations, which takes not-too-many-for-one-to-become-impatient seconds (for me less than a minute). Other programmers may realise it can be more efficient, say by creating a dictionary or hashmap from elements to array indices, but given the duration of the CTF, this was fast enough.

# Solution
[soln.py](soln.py)
```python
import re, pandas as pd

logs, qns = open('logs.txt').read().strip().split('\n'), open('questions.txt').read().strip().split('\n')

msgs, dts, sndrs, rcpnts = [], [], [], []
msg_re = re.compile(r'"[^"]+"')
dt_re = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')
sndr_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} sent | by [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')
rcpnt_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} was sent | to [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')

for line in logs: # 100,000
    msgs.append(msg_re.search(line).group(0))
    dts.append(dt_re.search(line).group(0))
    sndr, rcpnt = sndr_re.search(line).group(0), rcpnt_re.search(line).group(0)
    sndrs.append(sndr[4:] if sndr[0]==' ' else sndr[:-6]) # just user address, chop off surrounding excess
    rcpnts.append(rcpnt[4:] if rcpnt[0]==' ' else rcpnt[:-10]) # just user address, chop off surrounding excess

ans = []
usr_re = re.compile(r'[0-9a-f]{1,4}(:[0-9a-f]{1,4}){7}')
t1_re = re.compile(r'Who sent "[^"]+"')
t2_re = re.compile(r'Who did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} send "[^"]+"')
t3_re = re.compile(r'What did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} send at \d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')
t4_re = re.compile(r'Who did [0-9a-f]{1,4}(:[0-9a-f]{1,4}){7} receive a message from at \d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}')

for line in qns: # 5000 * 100,000
    if t1_re.match(line):
        msg = msg_re.search(line).group(0)
        for i in range(0, len(logs)):
            if msgs[i] == msg:
                ans.append(sndrs[i])
                break
    elif t2_re.match(line):
        sndr, msg = usr_re.search(line).group(0), msg_re.search(line).group(0)
        for i in range(0, len(logs)):
            if sndrs[i] == sndr and msgs[i] == msg:
                ans.append(rcpnts[i])
                break
    elif t3_re.match(line):
        sndr, dt = usr_re.search(line).group(0), dt_re.search(line).group(0)
        for i in range(0, len(logs)):
            if sndrs[i] == sndr and dts[i] == dt:
                ans.append(msgs[i][1:-1]) # chop off quotes
                break
    elif t4_re.match(line):
        rcpnt, dt = usr_re.search(line).group(0), dt_re.search(line).group(0)
        for i in range(0, len(logs)):
            if rcpnts[i] == rcpnt and dts[i] == dt:
                ans.append(sndrs[i])
                break

pd.DataFrame({'answer':ans}).to_csv('ans.csv', index = False)
```
**Answers:** [ans.csv](ans.csv)

# Credit
Directly copying the strings into an Excel file and converting to a CSV produced a presentation/formatting error when submitting. Thanks to @jloh02 for actually knowing how to use some pandas!
