import { Bot, Context, InlineKeyboard, session, SessionFlavor } from 'grammy';

// Define the session interface
interface SessionData {
  state: 'idle' | 'deposit' | 'withdraw';
  amount: number;
}

// Define the context type with session
type MyContext = Context & SessionFlavor<SessionData>;

// Create a new bot instance
const bot = new Bot<MyContext>('7472517699:AAEZ3qylDC3TCJhozhrc6OWIe9XATYezxHA');

console.log("starting server")

// Use session middleware
bot.use(session({
  initial: (): SessionData => ({
    state: 'idle',
    amount: 0,
  }),
}));
// Handle the /start command
bot.command('start', (ctx) => {
  const keyboard = new InlineKeyboard()
    .text('Deposit', 'deposit')
    .text('Withdraw', 'withdraw')
    .row()
    .text('Summary of Trade', 'summary');

  ctx.reply('Hello there! welcome to Whisper Finance.\nPlease select an option:', {
    reply_markup: keyboard,
  });
});

// Handle the deposit button
bot.callbackQuery('deposit', (ctx) => {
  ctx.session.state = 'deposit';
  ctx.reply('Please enter the deposit amount:');
});

// Handle the withdraw button
bot.callbackQuery('withdraw', (ctx) => {
  ctx.session.state = 'withdraw';
  ctx.reply('Please enter the withdrawal amount:');
});

// Handle the summary button
bot.callbackQuery('summary', (ctx) => {
  ctx.reply(`Trade summary:\nAmount: ${ctx.session.amount}`);
});

// Handle the user's input based on the current state
bot.on('message', (ctx) => {
  const sanitizedText = ctx.msg.text?.replace(/,/g, '');
  const amount = parseInt(sanitizedText || '0', 10);

  if (ctx.session.state === 'deposit') {
    if (amount > 0) {
      ctx.session.amount += amount;
      ctx.reply(`Deposit of ${amount} successful. Total balance: ${ctx.session.amount}`);
    } else {
      ctx.reply('Invalid deposit amount. Please enter a valid number.');
    }
    ctx.session.state = 'idle';
  } else if (ctx.session.state === 'withdraw') {
    if (amount > 0 && amount <= ctx.session.amount) {
      ctx.session.amount -= amount;
      ctx.reply(`Withdrawal of ${amount} successful. Remaining balance: ${ctx.session.amount}`);
    } else {
      ctx.reply(`Invalid withdrawal amount. Please enter a valid number within your balance.\nYour balance is ${ctx.session.amount}`);
    }
    ctx.session.state = 'idle';
  }
});

// Start the bot
bot.start();