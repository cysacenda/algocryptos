------------ NORMALIZATION ------------------

-- Table: public.coins
ALTER TABLE public.coins RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.coins RENAME COLUMN "Name" TO crypto_name;
ALTER TABLE public.coins RENAME COLUMN "Symbol" TO symbol;
ALTER TABLE public.coins RENAME COLUMN "CoinName" TO coin_name;
ALTER TABLE public.coins RENAME COLUMN "TotalCoinSupply" TO total_coin_supply;
ALTER TABLE public.coins RENAME COLUMN "SortOrder" TO sort_order;
ALTER TABLE public.coins RENAME COLUMN "ProofType" TO proof_type;
ALTER TABLE public.coins RENAME COLUMN "Algorithm" TO algorithm;
ALTER TABLE public.coins RENAME COLUMN "ImageUrl" TO image_url;

-- Table: public.prices
ALTER TABLE public.prices RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.prices RENAME COLUMN "Name" TO crypto_name;
ALTER TABLE public.prices RENAME COLUMN Rank TO crypto_rank;
ALTER TABLE public.prices RENAME COLUMN "24h_volume_usd" TO volume_usd_24h;

-- Table: public.social_infos
ALTER TABLE public.social_infos RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.social_infos RENAME COLUMN "Twitter_account_creation" TO twitter_account_creation;
ALTER TABLE public.social_infos RENAME COLUMN "Twitter_name" TO twitter_name;
ALTER TABLE public.social_infos RENAME COLUMN "Twitter_link" TO twitter_link;
ALTER TABLE public.social_infos RENAME COLUMN "Reddit_name" TO reddit_name;
ALTER TABLE public.social_infos RENAME COLUMN "Reddit_link" TO reddit_link;
ALTER TABLE public.social_infos RENAME COLUMN "Reddit_community_creation" TO reddit_community_creation;
ALTER TABLE public.social_infos RENAME COLUMN "Facebook_name" TO facebook_name;
ALTER TABLE public.social_infos RENAME COLUMN "Facebook_link" TO facebook_link;

-- Table: public.social_stats
ALTER TABLE public.social_stats RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.social_stats RENAME COLUMN "Twitter_followers" TO twitter_followers;
ALTER TABLE public.social_stats RENAME COLUMN "Reddit_posts_per_day" TO reddit_posts_per_day;
ALTER TABLE public.social_stats RENAME COLUMN "Reddit_comments_per_day" TO reddit_comments_per_day;
ALTER TABLE public.social_stats RENAME COLUMN "Reddit_active_users" TO reddit_active_users;
ALTER TABLE public.social_stats RENAME COLUMN "Reddit_subscribers" TO reddit_subscribers;
ALTER TABLE public.social_stats RENAME COLUMN "Facebook_likes" TO facebook_likes;
ALTER TABLE public.social_stats RENAME COLUMN "Facebook_talking_about" TO facebook_talking_about;

-- Table: public.social_stats_reddit
ALTER TABLE public.social_stats_reddit RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.social_stats_reddit RENAME COLUMN "Reddit_subscribers" TO reddit_subscribers;
ALTER TABLE public.social_stats_reddit RENAME COLUMN "Reddit_active_users" TO reddit_active_users;

-- Table: public.histo_ohlcv
ALTER TABLE public.histo_ohlcv RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.histo_ohlcv RENAME COLUMN "open" TO open_price;
ALTER TABLE public.histo_ohlcv RENAME COLUMN "high" TO high_price;
ALTER TABLE public.histo_ohlcv RENAME COLUMN "low" TO low_price;
ALTER TABLE public.histo_ohlcv RENAME COLUMN "close" TO close_price;

-- Table: public.excluded_coins
ALTER TABLE public.excluded_coins RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;

-- Table: public.social_infos_manual
ALTER TABLE public.social_infos_manual RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.social_infos_manual RENAME COLUMN "Reddit_name" TO reddit_name;
ALTER TABLE public.social_infos_manual RENAME COLUMN "Twitter_link" TO twitter_link;
ALTER TABLE public.social_infos_manual RENAME COLUMN "Facebook_link" TO facebook_link;

-- Table: public.histo_prices
ALTER TABLE public.histo_prices RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.histo_prices RENAME COLUMN "Name" TO crypto_name;
ALTER TABLE public.histo_prices RENAME COLUMN "24h_volume_usd" TO volume_usd_24h;

-- DROP TABLE public.kpi_reddit_subscribers;
ALTER TABLE public.kpi_reddit_subscribers RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;

-- Table: public.kpi_reddit_subscribers
ALTER TABLE public.kpi_reddit_subscribers_histo RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;

-- Table: public.process_params
ALTER TABLE public.process_params RENAME COLUMN "IdProcess" TO process_id;
ALTER TABLE public.process_params RENAME COLUMN "Name" TO process_name;
ALTER TABLE public.process_params RENAME COLUMN "Status" TO status;

-- Table: public.top_cryptos
ALTER TABLE public.top_cryptos RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;

-- Table: public.process_params_histo
ALTER TABLE public.process_params_histo RENAME COLUMN "IdProcess" TO process_id;
ALTER TABLE public.process_params_histo RENAME COLUMN "Name" TO process_name;
ALTER TABLE public.process_params_histo RENAME COLUMN "Status" TO status;

-- Table: public.social_stats_reddit_histo
ALTER TABLE public.social_stats_reddit_histo RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;
ALTER TABLE public.social_stats_reddit_histo RENAME COLUMN "Reddit_subscribers" TO reddit_subscribers;
ALTER TABLE public.social_stats_reddit_histo RENAME COLUMN "Reddit_active_users" TO reddit_active_users;

-- Table: public.global_data

-- Table: public.kpi_market_volumes;
ALTER TABLE public.kpi_market_volumes RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;

-- Table: public.kpi_market_volumes_histo;
ALTER TABLE public.kpi_market_volumes_histo RENAME COLUMN "IdCoinCryptoCompare" TO id_cryptocompare;

-- Table: public.lower_higher_prices
ALTER TABLE public.lower_higher_prices RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;

-- Table : public.process_description;
ALTER TABLE public.process_description RENAME COLUMN "Name" TO process_name;
ALTER TABLE public.process_description RENAME COLUMN "Description" TO description;

-- Table: public.social_google_trend
ALTER TABLE public.social_google_trend RENAME COLUMN "IdCryptoCompare" TO id_cryptocompare;

-------------

ALTER TABLE public.prices ADD COLUMN available_supply double precision;
