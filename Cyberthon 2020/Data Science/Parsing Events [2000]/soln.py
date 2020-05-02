import re, time as tm

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
