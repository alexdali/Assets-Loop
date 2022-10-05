from django.db.models import Count
from django.http import Http404
from django.views.generic import ListView

from banks.banks_config import BANKS_CONFIG
from banks.models import Banks
from crypto_exchanges.crypto_exchanges_registration.binance import (
    get_all, get_all_binance_crypto_exchanges,
    get_all_card_2_wallet_2_crypto_exchanges, get_all_p2p_binance_exchanges,
    get_best_card_2_card_crypto_exchanges, get_best_crypto_exchanges,
    get_binance_card_2_crypto_exchanges, get_binance_fiat_crypto_list,
    get_inter_exchanges_calculate)
from crypto_exchanges.models import (Card2CryptoExchanges,
                                     Card2Wallet2CryptoExchanges,
                                     CryptoExchanges, IntraCryptoExchanges,
                                     P2PCryptoExchangesRates,
                                     BestPaymentChannels,
                                     BestCombinationPaymentChannels,
                                     InterBankAndCryptoExchanges)
from django.db.models import F


class CryptoExchangesRatesList(ListView):
    def get_queryset(self):
        return self.model.objects.filter(price__isnull=False)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangesRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangeRatesList(ListView):
    def get_crypto_exchange_name(self):
        return self.kwargs.get('crypto_exchange_name').capitalize()

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                bank = Banks.objects.get(name=self.get_bank_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, bank=bank,
                    price__isnull=False
                )
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, price__isnull=False
                )
        else:
            bank = Banks.objects.get(name=self.get_bank_name())
            return self.model.objects.filter(bank=bank, price__isnull=False)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangesInternalExchanges(CryptoExchangesRatesList):
    model = IntraCryptoExchanges
    template_name = 'crypto_exchanges/internal_crypto_exchanges.html'


class CryptoExchangeInternalExchanges(CryptoExchangeRatesList):
    model = IntraCryptoExchanges
    template_name = 'crypto_exchanges/internal_crypto_exchanges.html'

    def get_queryset(self):
        crypto_exchange = CryptoExchanges.objects.get(
            name=self.get_crypto_exchange_name())
        return self.model.objects.filter(crypto_exchange=crypto_exchange)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class CryptoExchangesP2PExchanges(CryptoExchangesRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/p2p_crypto_exchanges.html'


class CryptoExchangeP2PExchanges(CryptoExchangeRatesList):
    model = P2PCryptoExchangesRates
    template_name = 'crypto_exchanges/p2p_crypto_exchanges.html'


class CryptoExchangesCard2Wallet2CryptoExchanges(CryptoExchangesRatesList):
    model = Card2Wallet2CryptoExchanges
    template_name = ('crypto_exchanges/'
                     'card_2_wallet_2_crypto_exchanges.html')


class CryptoExchangeCard2Wallet2CryptoExchanges(CryptoExchangeRatesList):
    model = Card2Wallet2CryptoExchanges
    template_name = ('crypto_exchanges/'
                     'card_2_wallet_2_crypto_exchanges.html')

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                transaction_methods = (
                    BANKS_CONFIG[self.get_bank_name()]['transaction_methods'])
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange,
                    transaction_method__in=transaction_methods,
                )
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange)
        else:
            transaction_methods = (
                BANKS_CONFIG[self.get_bank_name()]['transaction_methods'])
            return self.model.objects.filter(
                transaction_method__in=transaction_methods,
            )


class CryptoExchangesCard2CryptoExchanges(CryptoExchangesRatesList):
    model = Card2CryptoExchanges
    template_name = 'crypto_exchanges/card_2_crypto_exchanges.html'


class CryptoExchangeCard2CryptoExchanges(CryptoExchangeRatesList):
    model = Card2CryptoExchanges
    template_name = 'crypto_exchanges/card_2_crypto_exchanges.html'

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                payment_channels = (
                    BANKS_CONFIG[self.get_bank_name()]['payment_channels'])
                if self.model not in payment_channels:
                    raise Http404()
                currencies = BANKS_CONFIG[self.get_bank_name()]['currencies']
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange,
                    fiat__in=currencies)
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange)
        else:
            payment_channels = (
                BANKS_CONFIG[self.get_bank_name()]['payment_channels'])
            if self.model not in payment_channels:
                raise Http404()
            currencies = BANKS_CONFIG[self.get_bank_name()]['currencies']
            return self.model.objects.filter(fiat__in=currencies)


class CryptoExchangesBestPaymentChannelsExchanges(CryptoExchangesRatesList):
    model = BestPaymentChannels
    template_name = 'crypto_exchanges/best_crypto_exchanges.html'


class CryptoExchangeBestPaymentChannelsExchanges(CryptoExchangeRatesList):
    model = BestPaymentChannels
    template_name = 'crypto_exchanges/best_crypto_exchanges.html'


class IntraBanksCryptoExchangesCombinations(ListView):
    model = BestCombinationPaymentChannels
    template_name = ('crypto_exchanges/'
                     'intra_banks_exchanges_via_crypto_exchanges.html')

    def get_queryset(self):
        return self.model.objects.filter(input_bank=F('output_bank'))

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(IntraBanksCryptoExchangesCombinations,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class IntraBankCryptoExchangeCombinations(ListView):
    model = BestCombinationPaymentChannels
    template_name = ('crypto_exchanges/'
                     'intra_banks_exchanges_via_crypto_exchanges.html')

    def get_crypto_exchange_name(self):
        return self.kwargs.get('crypto_exchange_name').capitalize()

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                bank = Banks.objects.get(name=self.get_bank_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, input_bank=bank,
                    output_bank=bank
                )
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange)
        else:
            bank = Banks.objects.get(name=self.get_bank_name())
            return self.model.objects.filter(input_bank=bank, output_bank=bank)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(IntraBankCryptoExchangeCombinations,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(
            CRYPTO_EXCHANGES_CONFIG.keys()
            )[1:]
        context['crypto_exchange_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class InterBanksCryptoExchangesCombinations(
    IntraBanksCryptoExchangesCombinations
):
    template_name = ('crypto_exchanges/'
                     'inter_banks_exchanges_via_crypto_exchanges.html')

    def get_queryset(self):
        return self.model.objects.exclude(input_bank=F('output_bank'))


class InterBankCryptoExchangeCombinations(IntraBankCryptoExchangeCombinations):
    template_name = ('crypto_exchanges/'
                     'inter_banks_exchanges_via_crypto_exchanges.html')

    def get_bank_name(self):
        return self.kwargs.get('input_bank_name').capitalize()

    def get_end_bank_name(self):
        return self.kwargs.get('output_bank_name').capitalize()

    def get_queryset(self):
        if self.get_bank_name() != 'Input_banks':
            input_bank = Banks.objects.get(name=self.get_bank_name())
            if self. get_end_bank_name() != 'Output_banks':
                output_bank = Banks.objects.get(name=self.get_end_bank_name())
                if self.get_crypto_exchange_name() != 'Crypto_exchanges':
                    crypto_exchange = CryptoExchanges.objects.get(
                        name=self.get_crypto_exchange_name())
                    return self.model.objects.filter(
                        crypto_exchange=crypto_exchange, input_bank=input_bank,
                        output_bank=output_bank
                    ).exclude(input_bank=F('output_bank'))
                else:
                    return self.model.objects.filter(
                        input_bank=input_bank, output_bank=output_bank
                    ).exclude(input_bank=F('output_bank'))
            else:
                if self.get_crypto_exchange_name() != 'Crypto_exchanges':
                    crypto_exchange = CryptoExchanges.objects.get(
                        name=self.get_crypto_exchange_name())
                    return self.model.objects.filter(
                        crypto_exchange=crypto_exchange, input_bank=input_bank
                    ).exclude(input_bank=F('output_bank'))
                else:
                    return self.model.objects.filter(
                        input_bank=input_bank
                    ).exclude(input_bank=F('output_bank'))
        else:
            if self. get_end_bank_name() != 'Output_banks':
                output_bank = Banks.objects.get(name=self.get_end_bank_name())
                if self.get_crypto_exchange_name() != 'Crypto_exchanges':
                    crypto_exchange = CryptoExchanges.objects.get(
                        name=self.get_crypto_exchange_name())
                    return self.model.objects.filter(
                        crypto_exchange=crypto_exchange, output_bank=output_bank
                    ).exclude(input_bank=F('output_bank'))
                else:
                    return self.model.objects.filter(
                        output_bank=output_bank
                    ).exclude(input_bank=F('output_bank'))
            else:
                crypto_exchange = CryptoExchanges.objects.get(
                    name=self.get_crypto_exchange_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange
                ).exclude(input_bank=F('output_bank'))


class LoopInterCombinationsBanksAndCryptoExchanges(CryptoExchangesRatesList):
    model = InterBankAndCryptoExchanges
    template_name = ('crypto_exchanges/'
                     'loop_inter_banks_and_crypto_exchanges.html')

    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangesRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['loop_rates'] = self.get_queryset()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


class LoopInterCombinationsBankAndCryptoExchange(CryptoExchangeRatesList):
    model = InterBankAndCryptoExchanges
    template_name = ('crypto_exchanges/'
                     'loop_inter_banks_and_crypto_exchanges.html')

    def get_crypto_exchange_name(self):
        return self.kwargs.get('crypto_exchange_name').capitalize()

    def get_bank_name(self):
        return self.kwargs.get('bank_name').capitalize()

    def get_queryset(self):
        if self.get_crypto_exchange_name() != 'Crypto_exchanges':
            crypto_exchange = CryptoExchanges.objects.get(
                name=self.get_crypto_exchange_name())
            if self.get_bank_name() != 'Banks':
                bank = Banks.objects.get(name=self.get_bank_name())
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange, bank=bank
                )
            else:
                return self.model.objects.filter(
                    crypto_exchange=crypto_exchange
                )
        else:
            bank = Banks.objects.get(name=self.get_bank_name())
            return self.model.objects.filter(bank=bank)

    def get_context_data(self, **kwargs):
        from crypto_exchanges.crypto_exchanges_config import \
            CRYPTO_EXCHANGES_CONFIG
        context = super(CryptoExchangeRatesList,
                        self).get_context_data(**kwargs)
        context['bank_names'] = list(BANKS_CONFIG.keys())
        context['crypto_exchange_names'] = list(CRYPTO_EXCHANGES_CONFIG.keys()
                                                )[1:]
        context['loop_rates'] = self.get_queryset()
        context['crypto_exchange_name'] = self.get_crypto_exchange_name()
        context['bank_name'] = self.get_bank_name()
        context['last_update'] = self.get_queryset().latest(
            'update').update.updated
        return context


def p2p_binance(request):
    return get_all_p2p_binance_exchanges()


def binance_crypto(request):
    return get_all_binance_crypto_exchanges()


def card_2_wallet_2_crypto(request):
    return get_all_card_2_wallet_2_crypto_exchanges()


def binance_fiat_crypto_list(request):
    return get_binance_fiat_crypto_list()


def binance_card_2_crypto_exchanges(request):
    return get_binance_card_2_crypto_exchanges()


def binance_best_crypto_exchanges(request):
    return get_best_crypto_exchanges()


def binance_best_card_2_card_crypto_exchanges(request):
    return get_best_card_2_card_crypto_exchanges()


def binance_inter_exchanges_calculate(request):
    return get_inter_exchanges_calculate()


def all(request):
    return get_all()
