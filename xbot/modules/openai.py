import urllib.request
import re
import json

class OpenAIChat(object):

	def __init__(self, bot):
		self.bot = bot
		self.default_bot_prompt = "Friend"
		self.bot_prompt = self.default_bot_prompt
		self.default_chat_log = f"You: Hey friend\n{self.bot_prompt}: Hey again\n"
		self.start_chat_log = self.default_chat_log
		self.chat_log = None
		self.intro = ""

	def ask(self, question):
		if self.chat_log is None:
			self.chat_log = self.start_chat_log
		prompt = f'{self.intro}{self.chat_log}You: {question}\n{self.bot_prompt}:'
		body = {'prompt': prompt, 'model': "gpt-3.5-turbo-instruct", 'stop': "\nYou", 'temperature': 0.9, 'top_p': 1, 'frequency_penalty': 0, 'presence_penalty': 0.6, 'best_of': 1, 'max_tokens': 300}
		req = urllib.request.Request("https://api.openai.com/v1/completions", json.dumps(body).encode('utf8'), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % self.bot.config.get('module: openai', 'api_key')})
		try:
			answer = json.load(urllib.request.urlopen(req, timeout=10))['choices'][0]['text'].strip()
		except (TimeoutError, KeyError, IndexError) as e:
			return "%s: %s" % (e.__class__.__name__, e)
		except IOError as e:
			return "%s: %s" % (e, e.read().decode('utf8'))

		answer.replace("[insert your name here]", self.bot.name)

		self.append_interaction_to_chat_log(question, answer)

		return answer

	def append_interaction_to_chat_log(self, question, answer):
		if self.chat_log is None:
			chat_log = self.start_chat_log

		self.chat_log += f'{self.chat_log}You: {question}\n{self.bot_prompt}: {answer}\n'
		while len(self.chat_log) > 3500:
			index_of_you = self.chat_log.index("You:")
			if index_of_you == 0:
				index_of_you = self.chat_log.find("You:", 3)
			self.chat_log = self.chat_log[index_of_you:]

	def instance_set_prompt(self, bot_prompt, explanation, your_first_message, bot_first_reply):
		self.chat_log = None
		self.bot_prompt = bot_prompt.title()
		self.start_chat_log = f"You: {your_first_message}\n{self.bot_prompt}: {bot_first_reply}\n"
		self.intro = f"{explanation}\n\n"

	def reset(self):
		self.chat_log = None
		self.bot_prompt = self.default_bot_prompt
		self.start_chat_log = self.default_chat_log
		self.intro = ""

	def get_prompt(self):
		return "%s | %s | %s" % (self.bot_prompt, self.intro.strip() if self.intro else "No intro", ' | '.join(self.start_chat_log.splitlines()))

def set_prompt(bot, args):
	if 'openai' not in bot.inv:
		bot.inv['openai'] = {}
		if bot.remote['receiver'] not in bot.inv['openai']:
			bot.inv['openai'][bot.remote['receiver']] = OpenAIChat(bot)

	if len(args) == 2:
		if args[1] == "reset":
			bot.inv['openai'][bot.remote['receiver']].reset()
			return "!%s: Reset complete." % args[0]
		elif args[1] == "check":
			return "!%s: %s" % (args[0], bot.inv['openai'][bot.remote['receiver']].get_prompt())

	matches = re.match("^%s ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*)$" % args[0], ' '.join(args))
	if not matches:
		return "Usage: !%s [<bot_prompt>|check|reset] | <explanation> | <your_first_message> | <bot_first_reply>" % args[0]


	bot.inv['openai'][bot.remote['receiver']].instance_set_prompt(matches[1], matches[2], matches[3], matches[4])
	return "!%s: Prompt set complete. Prompt is '%s:'." % (args[0], matches[1])
