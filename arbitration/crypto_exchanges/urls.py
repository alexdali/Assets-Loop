from django.urls import include, path

from crypto_exchanges.views import (
    CryptoExchangeBestPaymentChannelsExchanges,
    CryptoExchangeCard2CryptoExchanges,
    CryptoExchangeCard2Wallet2CryptoExchanges, CryptoExchangeInternalExchanges,
    CryptoExchangeP2PExchanges, CryptoExchangesBestPaymentChannelsExchanges,
    CryptoExchangesCard2CryptoExchanges,
    CryptoExchangesCard2Wallet2CryptoExchanges,
    CryptoExchangesInternalExchanges, CryptoExchangesP2PExchanges,
    InterBankCryptoExchangeCombinations, InterBanksCryptoExchangesCombinations,
    IntraBankCryptoExchangeCombinations, IntraBanksCryptoExchangesCombinations,
    LoopInterCombinationsBankAndCryptoExchange,
    LoopInterCombinationsBanksAndCryptoExchanges, all,
    binance_best_card_2_card_crypto_exchanges, binance_best_crypto_exchanges,
    binance_card_2_crypto_exchanges, binance_crypto, binance_fiat_crypto_list,
    binance_inter_exchanges_calculate, card_2_wallet_2_crypto, p2p_binance,
    simpl_binance_tinkoff_inter_exchanges_calculate,
    complex_binance_tinkoff_inter_exchanges_calculate,
    complex_binance_wise_inter_exchanges_calculate, InterExchangesList)

from crypto_exchanges.views import get_wise_p2p_binance_exchanges, \
    get_tinkoff_p2p_binance_exchanges

app_name = 'crypto_exchanges'

urlpatterns = [
    path('crypto_exchanges/internal_crypto_exchanges/',
         CryptoExchangesInternalExchanges.as_view(),
         name='crypto_exchanges_internal_exchanges'),
    path('<str:crypto_exchange_name>/internal_crypto_exchanges/',
         CryptoExchangeInternalExchanges.as_view(),
         name='crypto_exchange_internal_exchanges'),
    path('crypto_exchanges/banks/p2p_exchanges/',
         CryptoExchangesP2PExchanges.as_view(),
         name='crypto_exchanges_p2p_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/p2p_exchanges/',
         CryptoExchangeP2PExchanges.as_view(),
         name='crypto_exchange_p2p_exchanges'),
    path('crypto_exchanges/banks/card_2_wallet_2_crypto_exchanges/',
         CryptoExchangesCard2Wallet2CryptoExchanges.as_view(),
         name='crypto_exchanges_card_2_wallet_2_crypto_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/'
         'card_2_wallet_2_crypto_exchanges/',
         CryptoExchangeCard2Wallet2CryptoExchanges.as_view(),
         name='crypto_exchange_card_2_wallet_2_crypto_exchanges'),
    path('crypto_exchanges/banks/card_2_crypto_exchanges/',
         CryptoExchangesCard2CryptoExchanges.as_view(),
         name='crypto_exchanges_card_2_crypto_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/card_2_crypto_exchanges/',
         CryptoExchangeCard2CryptoExchanges.as_view(),
         name='crypto_exchange_card_2_crypto_exchanges'),
    path('crypto_exchanges/banks/best_payment_channels_exchanges/',
         CryptoExchangesBestPaymentChannelsExchanges.as_view(),
         name='crypto_exchanges_best_payment_channels_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/'
         'best_payment_channels_exchanges/',
         CryptoExchangeBestPaymentChannelsExchanges.as_view(),
         name='crypto_exchange_best_payment_channels_exchanges'),
    path('crypto_exchanges/banks/intra_banks_exchanges_via_crypto_exchanges/',
         IntraBanksCryptoExchangesCombinations.as_view(),
         name='intra_banks_exchanges_via_crypto_exchanges_best_combinations'),
    path('<str:crypto_exchange_name>/<str:bank_name>/'
         'intra_banks_exchanges_via_crypto_exchanges/',
         IntraBankCryptoExchangeCombinations.as_view(),
         name='intra_bank_exchanges_via_crypto_exchange_best_combinations'),
    path('crypto_exchanges/input_banks/output_banks/'
         'inter_banks_exchanges_via_crypto_exchanges/',
         InterBanksCryptoExchangesCombinations.as_view(),
         name='inter_banks_exchanges_via_crypto_exchanges_best_combinations'),
    path('<str:crypto_exchange_name>/<str:input_bank_name>/'
         '<str:output_bank_name>/inter_banks_exchanges_via_crypto_exchanges/',
         InterBankCryptoExchangeCombinations.as_view(),
         name='inter_bank_exchanges_via_crypto_exchange_best_combinations'),
    path('crypto_exchanges/banks/loop_banks_and_crypto_exchanges/',
         LoopInterCombinationsBanksAndCryptoExchanges.as_view(),
         name='loop_inter_banks_and_crypto_exchanges'),
    path('<str:crypto_exchange_name>/<str:bank_name>/'
         'loop_banks_and_crypto_exchanges/',
         LoopInterCombinationsBankAndCryptoExchange.as_view(),
         name='loop_inter_bank_and_crypto_exchange'),
    path('inter-exchanges/',
         InterExchangesList.as_view(),
         name='InterExchangesList'),
    path('1/', get_tinkoff_p2p_binance_exchanges, name="get_tinkoff_p2p_binance_exchanges"),
    path('2/', get_wise_p2p_binance_exchanges, name="get_wise_p2p_binance_exchanges"),
    path('100/', binance_crypto, name="binance_crypto"),
    path('200/', card_2_wallet_2_crypto, name="binance_card_2_wallet_2_crypto"),
    path('300/', binance_fiat_crypto_list, name="binance_fiat_crypto_list"),
    path('400/', binance_card_2_crypto_exchanges,
         name="binance_card_2_crypto_exchanges"),
    path('500/', binance_best_crypto_exchanges,
         name="binance_best_crypto_exchanges"),
    path('600/', binance_best_card_2_card_crypto_exchanges,
         name="binance_best_card_2_card_crypto_exchanges"),
    path('700/', binance_inter_exchanges_calculate,
         name="binance_inter_exchanges_calculate"),
    path('1000/', all, name="all"),
    path('simpltin/', simpl_binance_tinkoff_inter_exchanges_calculate,
         name="simpl_binance_tinkoff_inter_exchanges_calculate"),
    path('complextin/', complex_binance_tinkoff_inter_exchanges_calculate,
         name="complex_binance_tinkoff_inter_exchanges_calculate"),
    path('complexwise/', complex_binance_wise_inter_exchanges_calculate,
         name="simpl_binance_tinkoff_inter_exchanges_calculate")
]
