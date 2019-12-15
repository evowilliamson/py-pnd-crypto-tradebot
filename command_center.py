import threading
from trade_engine import TradeEngine


class CommandCenter:

    def __init__(self, trade_engine):
        self._trade_engine = trade_engine
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def run(self):
        while True:
            input_console = input("> ")
            self.set_if_list_mode(input_console)

    def set_if_list_mode(self, input_console):
        command =  self.get_command(input_console)
        if command == "list":
            option = self.get_argument(input_console, 1)
            list_mode = None
            if option == TradeEngine.GAINERS:
                list_mode = TradeEngine.GAINERS
            elif option == TradeEngine.LOSERS:
                list_mode = TradeEngine.LOSERS
            else:
                self.print_incorrect_input(input_console)

            print("list mode set to: " + list_mode)
            self._trade_engine.change_list_mode(list_mode)

    @classmethod
    def get_command(cls, input_console):
        return input_console.split(" ")[0]

    @classmethod
    def get_argument(cls, input_console, argument_number):
        return input_console.split(" ")[argument_number]

    @classmethod
    def print_incorrect_input(cls, input_console):
        print("Error in input: " + input())

    def join(self):
        self._thread.join()

