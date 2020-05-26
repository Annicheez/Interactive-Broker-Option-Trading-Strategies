from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.scanner import ScannerSubscription
import threading


class StockScanner(EWrapper, EClient):

    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        self.contracts = []
        self.conids = []
        self.symbols = []

        # Connect to TWS
        self.connect(addr, port, client_id)
        self.count = 0

        # Launch the client thread
        thread = threading.Thread(target=self.run)
        thread.start()

    def scannerData(self, reqId, rank, Contractdetails,
                    distance, benchmark, projection, legsStr):

        print("Receiving Scanner Data", self.count)

        self.contracts.append(Contractdetails.contract)
        self.conids.append(Contractdetails.contract.conId)
        self.symbols.append(Contractdetails.contract.symbol)

        self.count += 1

    def scannerDataEnd(self, reqId):
        print('Number of results: {}'.format(self.count))
        self.cancelScannerSubscription(reqId)


    def error(self, reqId, code, msg):
        print('Error {}: {}'.format(code, msg))

def read_option_chain(MainClass, ScannerClass, ticker):

    # Define a contract for the underlying stock
    contract = Contract()
    contract.symbol = ticker
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    MainClass.reqContractDetails(0, contract)
    time.sleep(2)

    # Get the current price of the stock
    MainClass.reqTickByTickData(1, contract, "MidPoint", 1, True)
    time.sleep(4)

    # Request strike prices and expirations
    Scannerclass = client
    if Scannerclass.conids:
        Scannerclass.reqSecDefOptParams(2, ticker, '',
            'STK', Scannerclass.conid)
        time.sleep(2)
    else:
        print('Failed to obtain contract identifier.')
        exit()

    # Create contract for stock option
    req_id = 3
    if Scannerclass.strikes:
        for strike in Scannerclass.strikes:
            Scannerclass.chain[strike] = {}
            for right in ['C', 'P']:

                # Add to the option chain
                Scannerclass.chain[strike][right] = {}
                # Define the option contract
                contract.secType = 'OPT'
                contract.right = right
                contract.strike = strike
                contract.exchange = Scannerclass.exchange
                contract.lastTradeDateOrContractMonth =
                    Scannerclass.expiration

                # Request option data
                Scannerclass.reqMktData(req_id, contract,
                    '100', False, False, [])
                req_id += 1
                time.sleep(1)
    else:
        print('Failed to access strike prices')
        exit()
    time.sleep(5)

    # Remove empty elements
    for strike in client.chain:
        if client.chain[strike]['C'] == {} or
            client.chain[strike]['P'] == {}:
            client.chain.pop(strike)
    return client.chain, client.atm_price

