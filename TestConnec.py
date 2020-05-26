from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.scanner import ScannerSubscription
from Utilities import StockScanner
import pandas as pd
from typing import List
import datetime
import time


class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self,self)
        self.scanner_contract_list = []
        self.historical_data_master = pd.DataFrame({})

    def error(self, reqId, errorCode, errorString):
        print("Error", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print(contractDetails.__str__())

    def historicalData(self, reqId: int, bar):
        pd.set_option("display.max_columns", 500)

        historical_data_dict = {'con_id': reqId, 'date': bar.date, 'open': bar.open, 'high': bar.high,
                                'low': bar.low, 'close': bar.close, 'volume': bar.volume, 'average': bar.average,
                                'barcount': bar.barCount}
        historical_data = pd.DataFrame([historical_data_dict], columns=historical_data_dict.keys())

        self.historical_data_master = self.historical_data_master.append(historical_data)

        # print("HISTORICAL DATA", "\n", self.historical_data_master)

        result = pd.merge(self.historical_data_master,self.scanner_data_master, how='inner', on= 'con_id')

        print(result)


    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):

        super().scannerData(reqId, rank, contractDetails, distance, benchmark, projection, legsStr)

        self.scanner_contract_list.append(contractDetails.contract)


    # def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId,
    #                                       tradingClass, multiplier, expirations,
    #                                       strikes):
    #     super().securityDefinitionOptionParameter(reqId, exchange,
    #     underlyingConId, tradingClass, multiplier, expirations, strikes)
    #     ##________________________________________________________________________________________________________________##
    #     print("SecurityDefinitionOptionParameter.", "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:",
    #           underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier,
    #           "Expirations:", expirations, "Strikes:", str(strikes))

    def securityDefinitionOptionParameter(self, reqId:int, exchange:str,
        underlyingConId:int, tradingClass:str, multiplier:str,
        expirations, strikes):
        """ Returns the option chain for an underlying on an exchange
        specified in reqSecDefOptParams There will be multiple callbacks to
        securityDefinitionOptionParameter if multiple exchanges are specified
        in reqSecDefOptParams

        reqId - ID of the request initiating the callback
        underlyingConId - The conID of the underlying security
        tradingClass -  the option trading class
        multiplier -    the option multiplier
        expirations - a list of the expiries for the options of this underlying
             on this exchange
        strikes - a list of the possible strikes for options of this underlying
             on this exchange """

        print("SecurityDefinitionOptionParameter.", "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:",
                   underlyingConId, "TradingClass:", tradingClass, "Multiplier:", multiplier,
                   "Expirations:", expirations, "Strikes:", str(strikes))


    def scannerDataEnd(self, reqId):

        super().scannerDataEnd(reqId)

        print(len(self.scanner_contract_list))

        tradable_contracts : List[Contract] = self.scanner_contract_list[:11]            ## "Consider adding condition"

        for row in tradable_contracts:

            self.reqSecDefOptParams(row.conId, row.symbol, "SMART", row.secType, row.conId)

        self.cancelScannerSubscription(reqId)

    def scannerParameters(self, xml):
        super().scannerParameters(xml)
        open('log/scanner.xml', 'w').write(xml)
        print("Scanner Parameters received")


    def error_handler(msg):
        print("Server Error: %s" % msg)

    def reply_handler(msg):
        print("Server Response: %s, %s" % (msg.typeName, msg))


def main():
    
    ss = StockScanner("127.0.0.1", 7496, 0)

    scanner = ScannerSubscription()
    scanner.instrument = "STK"
    scanner.locationCode = "STK.US.MAJOR"
    scanner.scanCode = "HIGH_OPT_IMP_VOLAT"
    scanner.marketCapAbove = 5000000000
    scanner.averageOptionVolumeAbove = 50000

    ss.reqScannerSubscription(7001, scanner, [], [])
    time.sleep(2)
    print(len(ss.contracts))


if __name__ == "__main__":
    
    main()