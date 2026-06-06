import gradio as gr
from accounts import Account, get_share_price

# Create a single account instance
account = Account("Demo User")

def deposit_funds(amount):
    return account.deposit(amount)

def withdraw_funds(amount):
    return account.withdraw(amount)

def buy_shares(symbol, quantity):
    return account.buy_shares(symbol, quantity)

def sell_shares(symbol, quantity):
    return account.sell_shares(symbol, quantity)

def portfolio_value():
    return account.calculate_portfolio_value()

def profit_loss():
    return account.get_profit_loss()

def holdings():
    return account.get_holdings()

def transactions():
    return account.list_transactions()

# Gradio UI setup
with gr.Blocks() as demo:
    gr.Markdown("## Trading Simulation Account Management")
    
    with gr.Row():
        deposit_box = gr.Number(label="Deposit Amount")
        deposit_button = gr.Button("Deposit")
        deposit_output = gr.Textbox()
        deposit_button.click(deposit_funds, inputs=deposit_box, outputs=deposit_output)
        
    with gr.Row():
        withdraw_box = gr.Number(label="Withdraw Amount")
        withdraw_button = gr.Button("Withdraw")
        withdraw_output = gr.Textbox()
        withdraw_button.click(withdraw_funds, inputs=withdraw_box, outputs=withdraw_output)
        
    with gr.Row():
        buy_symbol = gr.Textbox(label="Buy Symbol (e.g., AAPL)")
        buy_quantity = gr.Number(label="Buy Quantity")
        buy_button = gr.Button("Buy Shares")
        buy_output = gr.Textbox()
        buy_button.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs=buy_output)
        
    with gr.Row():
        sell_symbol = gr.Textbox(label="Sell Symbol (e.g., AAPL)")
        sell_quantity = gr.Number(label="Sell Quantity")
        sell_button = gr.Button("Sell Shares")
        sell_output = gr.Textbox()
        sell_button.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs=sell_output)

    with gr.Row():
        value_button = gr.Button("Portfolio Value")
        value_output = gr.Label()
        value_button.click(portfolio_value, outputs=value_output)

    with gr.Row():
        profit_loss_button = gr.Button("Profit/Loss")
        profit_loss_output = gr.Label()
        profit_loss_button.click(profit_loss, outputs=profit_loss_output)

    with gr.Row():
        holdings_button = gr.Button("Get Holdings")
        holdings_output = gr.Textbox()
        holdings_button.click(holdings, outputs=holdings_output)

    with gr.Row():
        transactions_button = gr.Button("List Transactions")
        transactions_output = gr.Textbox()
        transactions_button.click(transactions, outputs=transactions_output)

demo.launch()