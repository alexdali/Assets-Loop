import math
import sys
from datetime import datetime
from itertools import permutations, product

from banks.models import (BankInvestExchanges, BankInvestExchangesUpdates,
                          Banks, BanksExchangeRates, BestBankExchanges,
                          BestBankExchangesUpdates, IntraBanksExchanges,
                          IntraBanksExchangesUpdates,
                          IntraBanksNotLoopedExchanges,
                          IntraBanksNotLoopedExchangesUpdates, CurrencyMarkets)
from crypto_exchanges.models import (BestCombinationPaymentChannels,
                                     BestCombinationPaymentChannelsUpdates,
                                     BestPaymentChannels,
                                     BestPaymentChannelsUpdates,
                                     Card2CryptoExchanges,
                                     Card2Wallet2CryptoExchanges,
                                     CryptoExchanges,
                                     InterBankAndCryptoExchanges,
                                     InterBankAndCryptoExchangesUpdates,
                                     IntraCryptoExchanges,
                                     P2PCryptoExchangesRates)
from django.core.exceptions import MultipleObjectsReturned


def get_related_exchange(meta_exchange):
    try:
        model = meta_exchange.payment_channel_model
    except AttributeError:
        model = meta_exchange.bank_exchange_model
    exchange_id = meta_exchange.exchange_id
    return getattr(sys.modules[__name__], model).objects.get(id=exchange_id)


class IntraBanks(object):
    bank_name = None
    fiats: tuple = None
    currencies_with_requisites = None
    percentage_round_to = 2

    def converts_choices_to_list(self) -> list:
        """repackaging choices of fiats into a list of fiats."""
        return list(choice[0] for choice in self.fiats)

    def create_iteration_combinations(self, combination):
        last = len(combination) - 1
        iteration_combinations = []
        for index_pair_first, fiat_pair_first in enumerate(combination):
            if index_pair_first == last:
                break
            for index_pair_second, fiat_pair_second in enumerate(combination):
                if index_pair_second == index_pair_first + 1:
                    fiat_pair = (fiat_pair_first, fiat_pair_second)
                    iteration_combinations.append(fiat_pair)
        return iteration_combinations

    def create_marginality_percentage(self, combination, all_exchanges):
        iteration_combinations = self.create_iteration_combinations(combination)
        iteration_prices = []
        for fiat_pair in iteration_combinations:
            fiat_pair_exchange = all_exchanges.get(from_fiat=fiat_pair[0],
                                                   to_fiat=fiat_pair[1])
            iteration_price = fiat_pair_exchange.price
            iteration_prices.append(iteration_price)
        accurate_marginality_percentage = math.prod(
            iteration_prices) * 100 - 100
        marginality_percentage = round(accurate_marginality_percentage,
                                       self.percentage_round_to)
        return marginality_percentage

    def add_to_bulk_update_or_create(
            self, bank, new_update, records_to_update, records_to_create,
            combination, marginality_percentage
    ):
        target_object = IntraBanksExchanges.objects.filter(
            bank=bank,
            list_of_transfers=combination
        )
        if target_object.exists():
            updated_object = IntraBanksExchanges.objects.get(
                bank=bank,
                list_of_transfers=combination
            )
            if updated_object.marginality_percentage == marginality_percentage:
                return
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraBanksExchanges(
                bank=bank,
                list_of_transfers=combination,
                marginality_percentage=marginality_percentage,
                update=new_update
            )
            records_to_create.append(created_object)

    def create_combinations(self, bank, new_update, all_exchanges,
                            records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        bank_config = BANKS_CONFIG.get(self.bank_name)
        all_fiats = bank_config.get('currencies')
        for initial_end_fiat in all_fiats:
            if initial_end_fiat not in self.currencies_with_requisites:
                continue
            combinable_fiats: list = list(bank_config.get('currencies'))
            combinable_fiats.remove(initial_end_fiat)
            for index in range(len(combinable_fiats)):
                if index == 2:
                    break
                body_combinations = list(permutations(combinable_fiats,
                                                      index + 1))
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, initial_end_fiat)
                    combination.append(initial_end_fiat)
                    marginality_percentage = self.create_marginality_percentage(
                        combination, all_exchanges
                    )
                    self.add_to_bulk_update_or_create(
                        bank, new_update, records_to_update, records_to_create,
                        combination, marginality_percentage
                    )

    def main(self):
        start_time = datetime.now()
        bank = Banks.objects.get(name=self.bank_name)
        new_update = IntraBanksExchangesUpdates.objects.create(bank=bank)
        all_exchanges = BanksExchangeRates.objects.all()
        records_to_update = []
        records_to_create = []
        self.create_combinations(
            bank, new_update, all_exchanges, records_to_update,
            records_to_create
        )
        IntraBanksExchanges.objects.bulk_create(records_to_create)
        IntraBanksExchanges.objects.bulk_update(
            records_to_update, ['marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class IntraBanksNotLooped(IntraBanks):
    bank_name = None

    def create_price_percentage_not_looped(self, bank, combination,
                                           all_exchanges):
        iteration_combinations = self.create_iteration_combinations(combination)
        iteration_prices = []
        for fiat_pair in iteration_combinations:
            fiat_pair_exchange = all_exchanges.get(
                from_fiat=fiat_pair[0], to_fiat=fiat_pair[1], bank=bank)
            iteration_price = fiat_pair_exchange.price
            iteration_prices.append(iteration_price)
        price = math.prod(iteration_prices)
        return price

    def create_marginality_percentage_not_looped(self, analogous_exchange_price,
                                                 price):
        accurate_marginality_percentage = price / (
                analogous_exchange_price / 100) - 100
        marginality_percentage = round(accurate_marginality_percentage,
                                       self.percentage_round_to)
        return marginality_percentage

    def add_to_bulk_update_or_create_not_looped(
            self, bank, new_update, records_to_update, records_to_create,
            combination, analogous_exchange, price, marginality_percentage
    ):
        target_object = IntraBanksNotLoopedExchanges.objects.filter(
            bank=bank,
            list_of_transfers=combination
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (
                    updated_object.marginality_percentage
                    == marginality_percentage and updated_object.price
                    == price
            ):
                return
            updated_object.price = price
            updated_object.marginality_percentage = marginality_percentage
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = IntraBanksNotLoopedExchanges(
                bank=bank,
                list_of_transfers=combination,
                from_fiat=combination[0],
                to_fiat=combination[-1],
                price=price,
                marginality_percentage=marginality_percentage,
                analogous_exchange=analogous_exchange,
                update=new_update
            )
            records_to_create.append(created_object)

    def create_combinations(self, bank, new_update, all_exchanges,
                            records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        bank_config = BANKS_CONFIG.get(self.bank_name)
        all_fiats = bank_config.get('currencies')
        input_fiats = output_fiats = bank_config.get('currencies')
        for input_fiat, output_fiat in product(input_fiats, output_fiats):
            duplicates_list = []
            combinable_fiats: list = list(all_fiats)
            combinable_fiats.remove(input_fiat)
            if input_fiat != output_fiat:
                combinable_fiats.remove(output_fiat)
            for index in range(len(combinable_fiats)):
                if index == 1:
                    break
                if input_fiat == output_fiat:
                    if input_fiat + str(index) in duplicates_list:
                        continue
                    else:
                        duplicates_list.append(input_fiat + str(index))
                body_combinations = list(permutations(combinable_fiats,
                                                      index + 1))
                for body_combination in body_combinations:
                    combination = list(body_combination)
                    combination.insert(0, input_fiat)
                    combination.append(output_fiat)
                    price = self.create_price_percentage_not_looped(
                        bank, combination, all_exchanges
                    )
                    if input_fiat != output_fiat:
                        analogous_exchange = all_exchanges.get(
                            from_fiat=input_fiat, to_fiat=output_fiat, bank=bank
                        )
                        analogous_exchange_price = analogous_exchange.price
                    else:
                        analogous_exchange = None
                        analogous_exchange_price = 1
                    marginality_percentage = (
                        self.create_marginality_percentage_not_looped(
                            analogous_exchange_price, price
                        )
                    )
                    self.add_to_bulk_update_or_create_not_looped(
                        bank, new_update, records_to_update, records_to_create,
                        combination, analogous_exchange, price,
                        marginality_percentage
                    )

    def main(self):
        start_time = datetime.now()
        bank = Banks.objects.get(name=self.bank_name)
        new_update = IntraBanksNotLoopedExchangesUpdates.objects.create(
            bank=bank)
        all_exchanges = BanksExchangeRates.objects.all()
        records_to_update = []
        records_to_create = []
        self.create_combinations(
            bank, new_update, all_exchanges, records_to_update,
            records_to_create
        )
        IntraBanksNotLoopedExchanges.objects.bulk_create(records_to_create)
        IntraBanksNotLoopedExchanges.objects.bulk_update(
            records_to_update, ['price', 'marginality_percentage', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BestCryptoExchanges(object):
    def __init__(self, crypto_exchange_name):
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=crypto_exchange_name
        )

    def add_to_bulk_update_or_create(
            self, bank, fiat, asset, trade_type, best_price,
            best_exchange_model, best_exchange_id, new_update,
            records_to_update, records_to_create
    ):
        target_object = BestPaymentChannels.objects.filter(
            crypto_exchange=self.crypto_exchange, bank=bank, fiat=fiat,
            asset=asset, trade_type=trade_type,
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (updated_object.payment_channel_model == best_exchange_model
                    and updated_object.exchange_id == best_exchange_id):
                if updated_object.price == best_price:
                    return
                new_update = updated_object.update
            updated_object.price = best_price
            updated_object.payment_channel_model = best_exchange_model
            updated_object.exchange_id = best_exchange_id
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BestPaymentChannels(
                crypto_exchange=self.crypto_exchange, bank=bank, fiat=fiat,
                asset=asset, trade_type=trade_type, price=best_price,
                payment_channel_model=best_exchange_model,
                exchange_id=best_exchange_id, update=new_update
            )
            records_to_create.append(created_object)

    def get_best_exchanges(self, new_update, records_to_update,
                           records_to_create):
        from banks.banks_config import BANKS_CONFIG
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        banks = BANKS_CONFIG.keys()
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        valid_payment_channels = crypto_exchanges_configs.get(
            'payment_channels')
        assets = crypto_exchanges_configs.get('assets')
        trade_types = crypto_exchanges_configs.get('trade_types')

        for bank_name in banks:
            bank = Banks.objects.get(name=bank_name)
            bank_configs = BANKS_CONFIG[bank_name]
            bank_payment_channels = bank_configs['payment_channels']
            bank_transaction_methods = bank_configs['transaction_methods']
            fiats = bank_configs['currencies']
            for fiat, asset, trade_type in product(fiats, assets, trade_types):
                exchanges_dict = {}
                for bank_payment_channel in bank_payment_channels:
                    if bank_payment_channel not in valid_payment_channels:
                        continue
                    checked_object = bank_payment_channel.objects.filter(
                        crypto_exchange=self.crypto_exchange,
                        trade_type=trade_type, fiat=fiat, asset=asset
                        )
                    if not checked_object.exists():
                        continue
                    elif (checked_object.__class__.__name__
                            == 'Card2Wallet2CryptoExchanges'
                            and checked_object.transaction_method
                            not in bank_transaction_methods):
                        continue
                    exchange = (checked_object.get(bank=bank)
                                if hasattr(bank_payment_channel, 'bank')
                                else checked_object.get())
                    price = exchange.price
                    if not price:
                        continue
                    exchange_info = (exchange.__class__.__name__, exchange.pk)
                    exchanges_dict[price] = exchange_info
                if not exchanges_dict:
                    continue
                best_price = max(exchanges_dict.keys())
                best_exchange_model = exchanges_dict[best_price][0]
                best_exchange_id = exchanges_dict[best_price][1]
                self.add_to_bulk_update_or_create(
                    bank, fiat, asset, trade_type, best_price,
                    best_exchange_model, best_exchange_id, new_update,
                    records_to_update, records_to_create
                )

    def main(self):
        start_time = datetime.now()
        new_update = BestPaymentChannelsUpdates.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_best_exchanges(
            new_update, records_to_update, records_to_create
        )
        BestPaymentChannels.objects.bulk_create(records_to_create)
        BestPaymentChannels.objects.bulk_update(
            records_to_update,
            ['price', 'payment_channel_model', 'exchange_id', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BestTotalCryptoExchanges(object):
    def __init__(self, crypto_exchange_name):
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=crypto_exchange_name
        )

    def add_to_bulk_update_or_create(
            self, new_update, records_to_update, records_to_create,
            best_total_price, best_total_exchange
    ):
        input_meta_exchange, interim_exchange, output_meta_exchange = (
            best_total_exchange)
        input_exchange = get_related_exchange(input_meta_exchange)
        input_bank = input_meta_exchange.bank
        from_fiat = input_exchange.fiat
        output_exchange = get_related_exchange(output_meta_exchange)
        output_bank = output_meta_exchange.bank
        to_fiat = output_exchange.fiat
        target_object = BestCombinationPaymentChannels.objects.filter(
            crypto_exchange=self.crypto_exchange, input_bank=input_bank,
            output_bank=output_bank, from_fiat=from_fiat, to_fiat=to_fiat,
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (updated_object.input_exchange == input_meta_exchange
                    and updated_object.output_exchange == output_meta_exchange):
                if updated_object.price == best_total_price:
                    return
                new_update = updated_object.update
            updated_object.price = best_total_price
            updated_object.input_exchange = input_meta_exchange
            updated_object.interim_exchange = interim_exchange
            updated_object.output_exchange = output_meta_exchange
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BestCombinationPaymentChannels(
                crypto_exchange=self.crypto_exchange, input_bank=input_bank,
                output_bank=output_bank, from_fiat=from_fiat, to_fiat=to_fiat,
                input_exchange=input_meta_exchange,
                interim_exchange=interim_exchange,
                output_exchange=output_meta_exchange, price=best_total_price,
                update=new_update
            )
            records_to_create.append(created_object)

    def get_best_total_exchanges(self, new_update,
                                 records_to_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        banks = BANKS_CONFIG.keys()
        for input_bank_name in banks:
            input_bank = Banks.objects.get(name=input_bank_name)
            input_meta_exchanges = BestPaymentChannels.objects.filter(
                crypto_exchange=self.crypto_exchange, bank=input_bank,
                trade_type='BUY'
            )
            output_meta_exchanges = BestPaymentChannels.objects.filter(
                crypto_exchange=self.crypto_exchange, trade_type='SELL'
            )
            exchanges_list = {}
            for input_meta_exchange, output_meta_exchange in product(
                    input_meta_exchanges, output_meta_exchanges):
                input_exchange = get_related_exchange(input_meta_exchange)
                input_fiat = input_exchange.fiat
                input_asset = input_exchange.asset
                input_price = input_exchange.price
                output_exchange = get_related_exchange(output_meta_exchange)
                output_fiat = output_exchange.fiat
                output_asset = output_exchange.asset
                output_price = output_exchange.price
                invalid_params_list = crypto_exchanges_configs.get(
                    'invalid_params_list')
                if ((input_asset, output_asset) in invalid_params_list
                        or (output_asset, input_asset) in invalid_params_list):
                    continue
                if not input_price or not output_price:
                    if not input_price:
                        input_meta_exchange.delete()
                    if not output_price:
                        output_meta_exchange.delete()
                    continue
                exchanges_name = input_fiat + output_fiat
                if not exchanges_list.get(exchanges_name):
                    exchanges_list[exchanges_name] = {}
                if input_asset != output_asset:
                    interim_exchange = IntraCryptoExchanges.objects.get(
                        crypto_exchange=self.crypto_exchange,
                        from_asset=input_asset, to_asset=output_asset
                    )
                    interim_price = interim_exchange.price
                else:
                    interim_exchange = None
                    interim_price = 1
                total_price = input_price * interim_price * output_price
                total_exchange = (
                    input_meta_exchange, interim_exchange, output_meta_exchange
                )
                exchanges_list[exchanges_name][total_price] = total_exchange

            for name, similar_exchanges in exchanges_list.items():
                best_total_price = max(similar_exchanges.keys())
                best_total_exchange = similar_exchanges[best_total_price]
                self.add_to_bulk_update_or_create(
                    new_update, records_to_update, records_to_create,
                    best_total_price, best_total_exchange
                )

    def main(self):
        start_time = datetime.now()
        new_update = BestCombinationPaymentChannelsUpdates.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        records_to_update = []
        records_to_create = []
        self.get_best_total_exchanges(
            new_update, records_to_update, records_to_create
        )
        BestCombinationPaymentChannels.objects.bulk_create(records_to_create)
        BestCombinationPaymentChannels.objects.bulk_update(
            records_to_update,
            ['price', 'input_exchange', 'interim_exchange',
             'output_exchange', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class InterExchangesCalculate(object):
    def __init__(self, crypto_exchange_name):
        self.crypto_exchange_name = crypto_exchange_name
        self.crypto_exchange = CryptoExchanges.objects.get(
            name=crypto_exchange_name
        )

    def get_list_crypt(self, crypto_rate):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        crypto_exchanges_configs = CRYPTO_EXCHANGES_CONFIG.get(
            self.crypto_exchange_name)
        list_crypto = []
        input_exchange = get_related_exchange(crypto_rate.input_exchange)
        input_fiat = input_exchange.fiat
        input_asset = input_exchange.asset
        input_price = input_exchange.price
        input_payment_channel = input_exchange.__class__.__name__
        if (input_payment_channel == 'P2PCryptoExchangesRates'
                or input_payment_channel == 'Card2CryptoExchanges'):
            list_crypto.append(
                [input_fiat, input_asset, input_payment_channel, input_price]
            )
        elif input_payment_channel == 'Card2Wallet2CryptoExchanges':
            input1_payment_channel, commission = crypto_exchanges_configs[
                'deposit_fiats'][input_fiat]
            input1_price = (100 - commission) / 100
            list_crypto.append(
                [input_fiat, input_fiat, input1_payment_channel, input1_price]
            )
            intra_exchange = IntraCryptoExchanges.objects.get(
                crypto_exchange=self.crypto_exchange, from_asset=input_fiat,
                to_asset=input_asset
            )
            input2_payment_channel = intra_exchange.__class__.__name__
            input2_price = intra_exchange.price
            list_crypto.append(
                [input_fiat, input_asset, input2_payment_channel, input2_price]
            )
        interim_exchange = crypto_rate.interim_exchange
        output_exchange = get_related_exchange(crypto_rate.output_exchange)
        output_asset = output_exchange.asset
        output_fiat = output_exchange.fiat
        output_price = output_exchange.price
        output_payment_channel = input_exchange.__class__.__name__
        if interim_exchange:
            interim_price = interim_exchange.price
            interim_payment_channel = interim_exchange.__class__.__name__
            list_crypto.append(
                [input_asset, output_asset,
                 interim_payment_channel, interim_price]
            )
        if (output_payment_channel == 'P2PCryptoExchangesRates'
                or output_payment_channel == 'Card2CryptoExchanges'):
            list_crypto.append(
                [output_asset, output_fiat,
                 output_payment_channel, output_price]
            )
        elif output_payment_channel == 'Card2Wallet2CryptoExchanges':
            intra_exchange = IntraCryptoExchanges.objects.get(
                crypto_exchange=self.crypto_exchange, from_asset=output_asset,
                to_asset=output_fiat
            )
            output1_payment_channel = intra_exchange.__class__.__name__
            output1_price = intra_exchange.price
            list_crypto.append(
                [output_asset, output_fiat,
                 output1_payment_channel, output1_price]
            )
            output2_payment_channel, commission = crypto_exchanges_configs[
                'withdraw_fiats'][output_fiat]
            output2_price = (100 - commission) / 100
            list_crypto.append(
                [output_fiat, output_fiat,
                 output2_payment_channel, output2_price]
            )
        return list_crypto

    def get_list_bank(self, bank_rate, bank):
        bank_exchange = get_related_exchange(bank_rate)
        from_fiat = bank_exchange.from_fiat
        to_fiat = bank_exchange.to_fiat
        price = bank_exchange.price
        bank_name = bank.name
        bank_exchange_type = bank_exchange.__class__.__name__
        if bank_exchange_type == 'BanksExchangeRates':
            return [from_fiat, to_fiat, bank_name, price]
        elif bank_exchange_type == 'BankInvestExchanges':
            invest_exchange_name = bank_exchange.currency_market.name
            return [from_fiat, to_fiat, bank_name,
                    f'invest exchange: {invest_exchange_name}', price]
        elif bank_exchange_type == 'IntraBanksNotLoopedExchanges':
            list_of_transfers = bank_exchange.list_of_transfers
            return [*list_of_transfers, bank_name, price]

    def add_to_bulk_create(
            self, new_update, records_to_create,
            crypto_rate, bank_rate, marginality_percentage
    ):
        InterBankAndCryptoExchanges.objects.all().delete()
        bank = bank_rate.bank
        list_bank_rate = self.get_list_bank(bank_rate, bank)
        list_crypto_rate = self.get_list_crypt(crypto_rate)
        created_object = InterBankAndCryptoExchanges(
            crypto_exchange=self.crypto_exchange, bank=bank,
            list_bank_rate=list_bank_rate, list_crypto_rate=list_crypto_rate,
            crypto_rate=crypto_rate, bank_rate=bank_rate,
            marginality_percentage=marginality_percentage, update=new_update
        )
        records_to_create.append(created_object)

    def calculate_marginality_percentage(self, new_update, records_to_create):
        from banks.banks_config import BANKS_CONFIG
        banks = BANKS_CONFIG.keys()
        for bank_name in banks:
            bank = Banks.objects.get(name=bank_name)
            crypto_rates = BestCombinationPaymentChannels.objects.filter(
                input_bank=bank, output_bank=bank
            )
            for crypto_rate in crypto_rates:
                crypto_rate_price = crypto_rate.price
                to_bank_fiat = crypto_rate.from_fiat
                from_bank_fiat = crypto_rate.to_fiat
                if to_bank_fiat == from_bank_fiat:
                    continue
                bank_rate = BestBankExchanges.objects.get(
                    bank=bank, from_fiat=from_bank_fiat, to_fiat=to_bank_fiat
                )
                bank_rate_price = bank_rate.price
                marginality_percentage = (crypto_rate_price *
                                          bank_rate_price - 1) * 100
                self.add_to_bulk_create(
                    new_update, records_to_create, crypto_rate, bank_rate,
                    marginality_percentage
                )

    def main(self):
        start_time = datetime.now()
        new_update = InterBankAndCryptoExchangesUpdates.objects.create(
            crypto_exchange=self.crypto_exchange
        )
        records_to_create = []
        self.calculate_marginality_percentage(
            new_update, records_to_create
        )
        InterBankAndCryptoExchanges.objects.bulk_create(records_to_create)
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()


class BestBankIntraExchanges(object):
    def __init__(self):
        bank = None
    def add_to_bulk_update_or_create(
            self, bank, from_fiat, to_fiat, best_price, best_exchange_model,
            best_exchange_id, new_update, records_to_update, records_to_create
    ):
        target_object = BestBankExchanges.objects.filter(
            bank=bank, from_fiat=from_fiat, to_fiat=to_fiat
        )
        if target_object.exists():
            updated_object = target_object.get()
            if (updated_object.bank_exchange_model == best_exchange_model
                    and updated_object.exchange_id == best_exchange_id):
                if updated_object.price == best_price:
                    return
                new_update = updated_object.update
            updated_object.price = best_price
            updated_object.bank_exchange_model = best_exchange_model
            updated_object.exchange_id = best_exchange_id
            updated_object.update = new_update
            records_to_update.append(updated_object)
        else:
            created_object = BestBankExchanges(
                bank=bank, from_fiat=from_fiat, to_fiat=to_fiat,
                price=best_price, bank_exchange_model=best_exchange_model,
                exchange_id=best_exchange_id, update=new_update
            )
            records_to_create.append(created_object)

    def get_best_exchanges(self, new_update, records_to_update,
                           records_to_create):
        from banks.banks_config import BANKS_CONFIG
        banks = BANKS_CONFIG.keys()
        for bank_name in banks:
            bank = Banks.objects.get(name=bank_name)
            bank_configs = BANKS_CONFIG[bank_name]
            bank_invests_names = bank_configs['bank_invest_exchanges']
            methods_exchanges = [
                BankInvestExchanges.objects.filter(
                    currency_market__name__in=bank_invests_names
                ),
                BanksExchangeRates.objects.filter(bank=bank),
                IntraBanksNotLoopedExchanges.objects.filter(
                    bank=bank, marginality_percentage__gt=0
                )
            ]
            fiats = bank_configs['currencies']
            for from_fiat, to_fiat in product(fiats, fiats):
                if from_fiat == to_fiat:
                    continue
                exchanges_dict = {}
                for exchanges in methods_exchanges:
                    if not exchanges:
                        continue
                    checked_object = exchanges.filter(from_fiat=from_fiat,
                                                      to_fiat=to_fiat)
                    if not checked_object.exists():
                        continue
                    try:
                        exchange = checked_object.get()
                    except MultipleObjectsReturned:
                        exchange = checked_object.order_by(
                            '-marginality_percentage'
                        )[0]
                    price = exchange.price
                    exchange_info = (exchange.__class__.__name__, exchange.pk)
                    exchanges_dict[price] = exchange_info
                if not exchanges_dict:
                    continue
                best_price = max(exchanges_dict.keys())
                best_exchange_model, best_exchange_id = exchanges_dict[
                    best_price]
                self.add_to_bulk_update_or_create(
                    bank, from_fiat, to_fiat, best_price, best_exchange_model,
                    best_exchange_id, new_update, records_to_update,
                    records_to_create
                )

    def main(self):
        start_time = datetime.now()
        new_update = BestBankExchangesUpdates.objects.create()
        records_to_update = []
        records_to_create = []
        self.get_best_exchanges(
            new_update, records_to_update, records_to_create
        )
        BestBankExchanges.objects.bulk_create(records_to_create)
        BestBankExchanges.objects.bulk_update(
            records_to_update,
            ['price', 'bank_exchange_model', 'exchange_id', 'update']
        )
        duration = datetime.now() - start_time
        new_update.duration = duration
        new_update.save()
