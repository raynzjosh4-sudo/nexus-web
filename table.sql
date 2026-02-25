-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.api_keys (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  key_name text NOT NULL UNIQUE,
  key_value text NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  last_used_at timestamp with time zone,
  CONSTRAINT api_keys_pkey PRIMARY KEY (id)
);
CREATE TABLE public.app_config (
  id integer NOT NULL DEFAULT 1,
  is_maintenance boolean DEFAULT false,
  CONSTRAINT app_config_pkey PRIMARY KEY (id)
);
CREATE TABLE public.app_versions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  platform text NOT NULL,
  latest_version text NOT NULL,
  force_update boolean DEFAULT false,
  store_url text,
  CONSTRAINT app_versions_pkey PRIMARY KEY (id)
);
CREATE TABLE public.bug_reports (
  id bigint NOT NULL DEFAULT nextval('bug_reports_id_seq'::regclass),
  user_id uuid NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  app_version text,
  device_info jsonb,
  stack_trace text,
  screenshot text,
  severity integer CHECK (severity >= 1 AND severity <= 5),
  status text DEFAULT 'open'::text CHECK (status = ANY (ARRAY['open'::text, 'in_progress'::text, 'resolved'::text, 'closed'::text])),
  tags ARRAY DEFAULT '{}'::text[],
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT bug_reports_pkey PRIMARY KEY (id),
  CONSTRAINT bug_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.business_categories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  pillar_id uuid,
  name text NOT NULL,
  tags ARRAY DEFAULT '{}'::text[],
  CONSTRAINT business_categories_pkey PRIMARY KEY (id),
  CONSTRAINT business_categories_pillar_id_fkey FOREIGN KEY (pillar_id) REFERENCES public.industry_pillars(id)
);
CREATE TABLE public.business_profiles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  business_name text NOT NULL,
  business_description text,
  business_address text,
  business_phone_number text,
  logo_url text,
  website_url text,
  category text,
  components jsonb,
  domain text UNIQUE,
  follower_count integer DEFAULT 0,
  following_count integer DEFAULT 0,
  average_rating numeric DEFAULT 0.0,
  total_reviews integer DEFAULT 0,
  logo_small_url text,
  cover_small_url text,
  category_pillar text,
  verify_category_piller text,
  status text DEFAULT 'draft'::text,
  last_activity_at timestamp with time zone DEFAULT now(),
  latitude numeric,
  longitude numeric,
  opening_hours jsonb,
  price_range text DEFAULT '$$'::text,
  place_name text,
  currency text DEFAULT 'UGX'::text,
  slug text,
  pillar_id uuid,
  is_verified boolean DEFAULT false,
  total_orders_completed integer DEFAULT 0,
  CONSTRAINT business_profiles_pkey PRIMARY KEY (id),
  CONSTRAINT business_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.business_specialties (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  specialty_name text NOT NULL UNIQUE,
  description text,
  created_at timestamp with time zone DEFAULT now(),
  pillar_id uuid,
  CONSTRAINT business_specialties_pkey PRIMARY KEY (id)
);
CREATE TABLE public.business_suggestion_carousels (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  carousel_type text NOT NULL,
  items ARRAY NOT NULL DEFAULT '{}'::jsonb[],
  item_count integer NOT NULL DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT business_suggestion_carousels_pkey PRIMARY KEY (id)
);
CREATE TABLE public.business_verifications (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  requirement_id uuid NOT NULL,
  status text NOT NULL DEFAULT 'pending'::text,
  file_url text,
  verified_at timestamp with time zone,
  notes text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT business_verifications_pkey PRIMARY KEY (id),
  CONSTRAINT business_verifications_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id),
  CONSTRAINT business_verifications_requirement_id_fkey FOREIGN KEY (requirement_id) REFERENCES public.verification_requirements(id)
);
CREATE TABLE public.cart_items (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  product_id uuid NOT NULL,
  quantity integer NOT NULL DEFAULT 1,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT cart_items_pkey PRIMARY KEY (id),
  CONSTRAINT cart_items_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.categories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT categories_pkey PRIMARY KEY (id)
);
CREATE TABLE public.category_requirements (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  category_id uuid,
  requirement_id uuid,
  is_mandatory boolean DEFAULT true,
  is_government_issued boolean DEFAULT true,
  CONSTRAINT category_requirements_pkey PRIMARY KEY (id),
  CONSTRAINT category_requirements_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.business_categories(id),
  CONSTRAINT category_requirements_requirement_id_fkey FOREIGN KEY (requirement_id) REFERENCES public.verification_requirements(id)
);
CREATE TABLE public.category_requirements_link (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  category_id uuid NOT NULL,
  requirement_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT category_requirements_link_pkey PRIMARY KEY (id),
  CONSTRAINT category_requirements_link_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.business_categories(id),
  CONSTRAINT category_requirements_link_requirement_id_fkey FOREIGN KEY (requirement_id) REFERENCES public.verification_requirements(id)
);
CREATE TABLE public.chat_messages (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  room_id uuid NOT NULL,
  sender_id uuid NOT NULL,
  message text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT chat_messages_pkey PRIMARY KEY (id),
  CONSTRAINT chat_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.nexususers(id),
  CONSTRAINT chat_messages_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.chat_rooms(id)
);
CREATE TABLE public.chat_room_participants (
  chat_room_id uuid NOT NULL,
  user_id uuid NOT NULL,
  joined_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT chat_room_participants_pkey PRIMARY KEY (chat_room_id, user_id),
  CONSTRAINT chat_room_participants_chat_room_id_fkey FOREIGN KEY (chat_room_id) REFERENCES public.chat_rooms(id),
  CONSTRAINT chat_room_participants_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.chat_rooms (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  business_id uuid,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  name text,
  is_group boolean DEFAULT false,
  related_item_id uuid UNIQUE,
  avatar_url text,
  metadata jsonb DEFAULT '{}'::jsonb,
  updated_at timestamp with time zone DEFAULT now(),
  last_message text,
  last_message_time timestamp with time zone DEFAULT now(),
  participant_ids ARRAY DEFAULT '{}'::uuid[],
  market_order_id uuid UNIQUE,
  CONSTRAINT chat_rooms_pkey PRIMARY KEY (id),
  CONSTRAINT chat_rooms_related_item_id_fkey FOREIGN KEY (related_item_id) REFERENCES public.swap_items(id),
  CONSTRAINT chat_rooms_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id),
  CONSTRAINT chat_rooms_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id),
  CONSTRAINT chat_rooms_market_order_id_fkey FOREIGN KEY (market_order_id) REFERENCES public.market_orders(id)
);
CREATE TABLE public.comment_likes (
  user_id uuid NOT NULL,
  comment_id uuid NOT NULL,
  post_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT comment_likes_pkey PRIMARY KEY (user_id, comment_id),
  CONSTRAINT comment_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT comment_likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id)
);
CREATE TABLE public.comments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  post_id uuid NOT NULL,
  user_id uuid NOT NULL,
  text text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT comments_pkey PRIMARY KEY (id),
  CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id),
  CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.community_comments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  post_id uuid NOT NULL,
  author_id uuid NOT NULL,
  parent_id uuid,
  content text NOT NULL,
  attachment_type text DEFAULT 'text'::text,
  attachment_url text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT community_comments_pkey PRIMARY KEY (id),
  CONSTRAINT community_comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.community_posts(id),
  CONSTRAINT community_comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.community_comments(id),
  CONSTRAINT community_comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.community_post_recommendations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  post_id uuid NOT NULL,
  author_id uuid NOT NULL,
  recommendation_title text NOT NULL,
  recommendation_body text,
  business_profile_id uuid,
  image_url text,
  location_name text DEFAULT 'Kampala, Uganda'::text,
  created_at timestamp with time zone DEFAULT now(),
  contact_phone text,
  rating numeric DEFAULT 0.0,
  CONSTRAINT community_post_recommendations_pkey PRIMARY KEY (id),
  CONSTRAINT fk_original_post FOREIGN KEY (post_id) REFERENCES public.community_posts(id),
  CONSTRAINT fk_recommendation_author FOREIGN KEY (author_id) REFERENCES public.nexususers(id),
  CONSTRAINT fk_linked_business FOREIGN KEY (business_profile_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.community_posts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  author_id uuid NOT NULL,
  title text NOT NULL,
  body text NOT NULL,
  category text NOT NULL,
  location text DEFAULT 'Kampala, Uganda'::text,
  image_url text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  reply_count integer DEFAULT 0,
  view_count integer DEFAULT 0,
  fts tsvector DEFAULT to_tsvector('english'::regconfig, ((COALESCE(title, ''::text) || ' '::text) || COALESCE(body, ''::text))),
  slug text UNIQUE,
  share_link text,
  CONSTRAINT community_posts_pkey PRIMARY KEY (id),
  CONSTRAINT community_posts_author_id_fkey FOREIGN KEY (author_id) REFERENCES auth.users(id),
  CONSTRAINT community_posts_nexususers_fkey FOREIGN KEY (author_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.deleted_messages (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  message_id uuid,
  user_id uuid,
  deleted_at timestamp with time zone DEFAULT now(),
  CONSTRAINT deleted_messages_pkey PRIMARY KEY (id),
  CONSTRAINT deleted_messages_message_id_fkey FOREIGN KEY (message_id) REFERENCES public.messages(id),
  CONSTRAINT deleted_messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.deletion_surveys (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  reason text,
  frustrating_feature text,
  recommend_score text,
  support_experience text,
  retention_what_needed text,
  text_feedback text,
  created_at timestamp with time zone DEFAULT now(),
  email text,
  name text,
  avatar_url text,
  CONSTRAINT deletion_surveys_pkey PRIMARY KEY (id),
  CONSTRAINT deletion_surveys_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.error_logs (
  id integer NOT NULL DEFAULT nextval('error_logs_id_seq'::regclass),
  created_at timestamp with time zone DEFAULT now(),
  error text,
  stack_trace text,
  user_id uuid,
  feature_name text,
  context jsonb DEFAULT '{}'::jsonb,
  CONSTRAINT error_logs_pkey PRIMARY KEY (id),
  CONSTRAINT error_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.event_attendees (
  event_id uuid NOT NULL,
  user_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT event_attendees_pkey PRIMARY KEY (event_id, user_id),
  CONSTRAINT event_attendees_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.community_posts(id),
  CONSTRAINT event_attendees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.flash_sale_carousels (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  carousel_index integer NOT NULL DEFAULT 0,
  items ARRAY NOT NULL DEFAULT '{}'::jsonb[],
  item_count integer NOT NULL DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT flash_sale_carousels_pkey PRIMARY KEY (id),
  CONSTRAINT flash_sale_carousels_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.followers (
  user_id uuid NOT NULL,
  business_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT followers_pkey PRIMARY KEY (user_id, business_id),
  CONSTRAINT followers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id),
  CONSTRAINT followers_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.industry_pillars (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL UNIQUE,
  icon_key text NOT NULL,
  description text,
  CONSTRAINT industry_pillars_pkey PRIMARY KEY (id)
);
CREATE TABLE public.lost_found_items (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  reporter_id uuid NOT NULL,
  title text NOT NULL,
  description text,
  category text NOT NULL,
  image_url text,
  show_image boolean DEFAULT true,
  is_sensitive boolean DEFAULT false,
  is_anonymous boolean DEFAULT false,
  status USER-DEFINED NOT NULL,
  item_date timestamp with time zone DEFAULT now(),
  custody_type USER-DEFINED DEFAULT 'other'::custody_type,
  custody_location_name text,
  location_coordinates USER-DEFINED NOT NULL,
  reward_amount numeric DEFAULT 0.0,
  contact_method USER-DEFINED DEFAULT 'inAppChat'::contact_method,
  contact_value text,
  key_attributes jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  view_count integer DEFAULT 0,
  fts tsvector DEFAULT to_tsvector('english'::regconfig, ((((COALESCE(title, ''::text) || ' '::text) || COALESCE(description, ''::text)) || ' '::text) || COALESCE(category, ''::text))),
  location_name text,
  slug text UNIQUE,
  CONSTRAINT lost_found_items_pkey PRIMARY KEY (id),
  CONSTRAINT lost_found_items_reporter_id_fkey FOREIGN KEY (reporter_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.market_orders (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT timezone('utc'::text, now()),
  buyer_id uuid NOT NULL,
  business_id uuid,
  product_id uuid NOT NULL,
  category_id text,
  order_type text NOT NULL,
  offer_price numeric NOT NULL,
  payment_method text DEFAULT 'CASH'::text,
  status text DEFAULT 'PENDING'::text,
  buyer_phone text,
  buyer_lat double precision,
  buyer_long double precision,
  note text,
  terms_conditions text,
  readable_id bigint DEFAULT nextval('order_number_seq'::regclass),
  estimated_delivery_at timestamp with time zone,
  tracking_url text,
  currency text DEFAULT 'UGX'::text,
  preferences jsonb DEFAULT '{}'::jsonb,
  CONSTRAINT market_orders_pkey PRIMARY KEY (id),
  CONSTRAINT market_orders_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES auth.users(id),
  CONSTRAINT market_orders_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.posts(id),
  CONSTRAINT market_orders_buyer_id_fkey_nexus FOREIGN KEY (buyer_id) REFERENCES public.nexususers(id),
  CONSTRAINT fk_market_orders_business_profile FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.messages (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  chat_room_id uuid NOT NULL,
  sender_id uuid NOT NULL,
  content text,
  media_url text,
  reply_to_message_id uuid,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  metadata jsonb DEFAULT '{}'::jsonb,
  type text DEFAULT 'text'::text,
  CONSTRAINT messages_pkey PRIMARY KEY (id),
  CONSTRAINT messages_chat_room_id_fkey FOREIGN KEY (chat_room_id) REFERENCES public.chat_rooms(id),
  CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES auth.users(id)
);
CREATE TABLE public.news_articles (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  title text NOT NULL,
  description text NOT NULL,
  content text NOT NULL,
  image_url text NOT NULL,
  image_urls ARRAY DEFAULT '{}'::text[],
  source_url text,
  author_id uuid NOT NULL,
  category USER-DEFINED NOT NULL,
  published_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone,
  view_count integer DEFAULT 0,
  like_count integer DEFAULT 0,
  share_count integer DEFAULT 0,
  comment_count integer DEFAULT 0,
  tags ARRAY DEFAULT '{}'::text[],
  sentiment numeric,
  related_article_ids ARRAY DEFAULT '{}'::uuid[],
  source text,
  is_featured boolean DEFAULT false,
  read_time_minutes integer DEFAULT 5,
  CONSTRAINT news_articles_pkey PRIMARY KEY (id),
  CONSTRAINT news_articles_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.news_authors(id)
);
CREATE TABLE public.news_authors (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  name text NOT NULL,
  avatar_url text NOT NULL,
  title text,
  organization text,
  followers_count integer DEFAULT 0,
  is_verified boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT news_authors_pkey PRIMARY KEY (id)
);
CREATE TABLE public.news_comments (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  article_id uuid NOT NULL,
  author_id uuid NOT NULL,
  text text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone,
  like_count integer DEFAULT 0,
  parent_comment_id uuid,
  CONSTRAINT news_comments_pkey PRIMARY KEY (id),
  CONSTRAINT news_comments_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id),
  CONSTRAINT news_comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.news_authors(id),
  CONSTRAINT news_comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.news_comments(id)
);
CREATE TABLE public.nexus_launch_assets (
  id integer NOT NULL DEFAULT nextval('nexus_launch_assets_id_seq'::regclass),
  config_name text DEFAULT 'default_loading'::text UNIQUE,
  upper_url text,
  bellow_url text,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT nexus_launch_assets_pkey PRIMARY KEY (id)
);
CREATE TABLE public.nexususers (
  id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  name text,
  email text,
  phone_number text,
  avatar_url text,
  role USER-DEFINED DEFAULT 'buyer'::user_role,
  is_verified boolean DEFAULT false,
  rating numeric DEFAULT 0.0,
  swaps_count integer DEFAULT 0,
  trust_score numeric DEFAULT 0.0,
  bio text,
  social_links jsonb DEFAULT '{}'::jsonb,
  follower_count integer DEFAULT 0,
  following_count integer DEFAULT 0,
  is_influencer boolean DEFAULT false,
  accepted_swap_policy boolean DEFAULT false,
  slug text UNIQUE,
  share_link text,
  is_admin boolean DEFAULT false,
  CONSTRAINT nexususers_pkey PRIMARY KEY (id),
  CONSTRAINT nexususers_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id)
);
CREATE TABLE public.notifications (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  title text NOT NULL,
  body text,
  type text,
  is_read boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  actor_avatar_url text,
  target_id text,
  related_image_url text,
  actor_name text,
  image_url text,
  actor_id uuid,
  data jsonb DEFAULT '{}'::jsonb,
  CONSTRAINT notifications_pkey PRIMARY KEY (id),
  CONSTRAINT notifications_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES auth.users(id),
  CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.post_comments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  post_id uuid,
  user_id uuid,
  author_name text,
  author_image_url text,
  comment_text text,
  created_at timestamp with time zone DEFAULT now(),
  media_url text,
  media_type text,
  CONSTRAINT post_comments_pkey PRIMARY KEY (id),
  CONSTRAINT post_comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id),
  CONSTRAINT post_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.post_stats (
  post_id uuid NOT NULL,
  order_count integer DEFAULT 0,
  view_count integer DEFAULT 0,
  share_count integer DEFAULT 0,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT post_stats_pkey PRIMARY KEY (post_id),
  CONSTRAINT post_stats_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id)
);
CREATE TABLE public.post_views (
  user_id uuid NOT NULL,
  post_id uuid NOT NULL,
  CONSTRAINT post_views_pkey PRIMARY KEY (user_id, post_id),
  CONSTRAINT post_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT post_views_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.community_posts(id)
);
CREATE TABLE public.posts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  type text NOT NULL,
  data jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  user_id uuid,
  category_id uuid,
  fts tsvector,
  image_labels ARRAY,
  wish_count integer DEFAULT 0,
  comment_count integer DEFAULT 0,
  order_count integer DEFAULT 0,
  slug text UNIQUE,
  title text,
  price numeric DEFAULT 0,
  currency text DEFAULT 'UGX'::text,
  stock_status text DEFAULT 'in_stock'::text,
  share_link text,
  ai_generated boolean DEFAULT false,
  carousel_id uuid,
  carousel_index integer,
  CONSTRAINT posts_pkey PRIMARY KEY (id),
  CONSTRAINT posts_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id),
  CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT posts_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id)
);
CREATE TABLE public.reports (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  reporter_id uuid,
  reported_user_id uuid,
  content_id text,
  reason text NOT NULL,
  status text DEFAULT 'pending'::text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT reports_pkey PRIMARY KEY (id),
  CONSTRAINT reports_reporter_id_fkey FOREIGN KEY (reporter_id) REFERENCES auth.users(id)
);
CREATE TABLE public.requirement_rules (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  requirement_name text NOT NULL,
  requirement_description text,
  target_pillar_id uuid,
  target_tag text,
  is_mandatory boolean DEFAULT true,
  CONSTRAINT requirement_rules_pkey PRIMARY KEY (id),
  CONSTRAINT requirement_rules_target_pillar_id_fkey FOREIGN KEY (target_pillar_id) REFERENCES public.industry_pillars(id)
);
CREATE TABLE public.reviews (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  product_id uuid NOT NULL,
  rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT reviews_pkey PRIMARY KEY (id),
  CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.roads (
  id integer NOT NULL DEFAULT nextval('roads_id_seq'::regclass),
  osm_id bigint,
  source integer,
  target integer,
  cost_len double precision,
  geom USER-DEFINED,
  CONSTRAINT roads_pkey PRIMARY KEY (id)
);
CREATE TABLE public.short_video_carousels (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  carousel_index integer NOT NULL DEFAULT 0,
  items ARRAY NOT NULL DEFAULT '{}'::jsonb[],
  item_count integer NOT NULL DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT short_video_carousels_pkey PRIMARY KEY (id),
  CONSTRAINT short_video_carousels_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.spatial_ref_sys (
  srid integer NOT NULL CHECK (srid > 0 AND srid <= 998999),
  auth_name character varying,
  auth_srid integer,
  srtext character varying,
  proj4text character varying,
  CONSTRAINT spatial_ref_sys_pkey PRIMARY KEY (srid)
);
CREATE TABLE public.stories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  media_url text NOT NULL,
  caption text,
  created_at timestamp with time zone DEFAULT now(),
  expires_at timestamp with time zone DEFAULT (now() + '24:00:00'::interval),
  CONSTRAINT stories_pkey PRIMARY KEY (id),
  CONSTRAINT stories_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.story_replies (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL,
  sender_id uuid NOT NULL,
  receiver_id uuid NOT NULL,
  message text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  read_at timestamp with time zone,
  CONSTRAINT story_replies_pkey PRIMARY KEY (id),
  CONSTRAINT story_replies_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.nexususers(id),
  CONSTRAINT story_replies_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.nexususers(id),
  CONSTRAINT story_replies_business_id_fkey FOREIGN KEY (business_id) REFERENCES public.business_profiles(id)
);
CREATE TABLE public.story_views (
  story_id uuid NOT NULL,
  viewer_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT story_views_pkey PRIMARY KEY (story_id, viewer_id),
  CONSTRAINT story_views_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.posts(id),
  CONSTRAINT story_views_viewer_id_fkey FOREIGN KEY (viewer_id) REFERENCES auth.users(id)
);
CREATE TABLE public.support_messages (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  ticket_id uuid NOT NULL,
  sender_id uuid,
  message text NOT NULL,
  is_from_admin boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  message_type text DEFAULT 'text'::text CHECK (message_type = ANY (ARRAY['text'::text, 'image'::text, 'video'::text, 'voice'::text, 'media'::text])),
  media_url text,
  voice_url text,
  voice_duration integer,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT support_messages_pkey PRIMARY KEY (id),
  CONSTRAINT support_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES auth.users(id),
  CONSTRAINT support_messages_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.support_tickets(id)
);
CREATE TABLE public.support_tickets (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  subject text DEFAULT 'App Support'::text,
  status text DEFAULT 'open'::text CHECK (status = ANY (ARRAY['open'::text, 'pending'::text, 'resolved'::text])),
  created_at timestamp with time zone DEFAULT now(),
  last_message text,
  description text,
  priority text DEFAULT 'medium'::text CHECK (priority = ANY (ARRAY['low'::text, 'medium'::text, 'high'::text, 'urgent'::text])),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT support_tickets_pkey PRIMARY KEY (id),
  CONSTRAINT support_tickets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.swap_items (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  owner_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  title text NOT NULL,
  description text,
  category text,
  condition text DEFAULT 'Used'::text,
  estimated_value numeric DEFAULT 0,
  image_urls ARRAY DEFAULT '{}'::text[],
  want_title text,
  view_count integer DEFAULT 0,
  is_active boolean DEFAULT true,
  location_name text,
  search_vector tsvector,
  location_data jsonb,
  have_category_id uuid,
  want_category_id uuid,
  group_chat_id uuid,
  currency_code text DEFAULT 'USD'::text,
  currency_symbol text DEFAULT '$'::text,
  slug text UNIQUE,
  trade_preference text DEFAULT 'open'::text,
  status text DEFAULT 'available'::text,
  CONSTRAINT swap_items_pkey PRIMARY KEY (id),
  CONSTRAINT swap_items_group_chat_id_fkey FOREIGN KEY (group_chat_id) REFERENCES public.chat_rooms(id),
  CONSTRAINT swap_items_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.nexususers(id),
  CONSTRAINT swap_items_have_category_id_fkey FOREIGN KEY (have_category_id) REFERENCES public.categories(id),
  CONSTRAINT swap_items_want_category_id_fkey FOREIGN KEY (want_category_id) REFERENCES public.categories(id)
);
CREATE TABLE public.swap_offers (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  sender_id uuid NOT NULL,
  receiver_id uuid,
  sender_item_id uuid,
  receiver_item_id uuid,
  cash_adjustment numeric DEFAULT 0,
  status text DEFAULT 'pending'::text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  accepted_by_ids jsonb DEFAULT '[]'::jsonb,
  required_ids jsonb DEFAULT '[]'::jsonb,
  trade_type text DEFAULT 'Direct'::text,
  rating_given integer,
  CONSTRAINT swap_offers_pkey PRIMARY KEY (id),
  CONSTRAINT swap_offers_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.nexususers(id),
  CONSTRAINT swap_offers_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.nexususers(id),
  CONSTRAINT swap_offers_sender_item_id_fkey FOREIGN KEY (sender_item_id) REFERENCES public.swap_items(id),
  CONSTRAINT swap_offers_receiver_item_id_fkey FOREIGN KEY (receiver_item_id) REFERENCES public.swap_items(id)
);
CREATE TABLE public.swap_watchlist (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  item_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT swap_watchlist_pkey PRIMARY KEY (id),
  CONSTRAINT swap_watchlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id),
  CONSTRAINT swap_watchlist_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.swap_items(id)
);
CREATE TABLE public.trending_topics (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  title text NOT NULL,
  article_count integer DEFAULT 0,
  mention_count integer DEFAULT 0,
  trending_score numeric DEFAULT 0.0,
  trending_since timestamp with time zone DEFAULT now(),
  image_url text,
  related_tags ARRAY DEFAULT '{}'::text[],
  CONSTRAINT trending_topics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_article_bookmarks (
  user_id uuid NOT NULL,
  article_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_article_bookmarks_pkey PRIMARY KEY (user_id, article_id),
  CONSTRAINT user_article_bookmarks_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT user_article_bookmarks_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id)
);
CREATE TABLE public.user_article_likes (
  user_id uuid NOT NULL,
  article_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_article_likes_pkey PRIMARY KEY (user_id, article_id),
  CONSTRAINT user_article_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT user_article_likes_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.news_articles(id)
);
CREATE TABLE public.user_blocks (
  blocker_id uuid NOT NULL,
  blocked_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_blocks_pkey PRIMARY KEY (blocker_id, blocked_id),
  CONSTRAINT user_blocks_blocker_id_fkey FOREIGN KEY (blocker_id) REFERENCES auth.users(id)
);
CREATE TABLE public.user_comment_likes (
  user_id uuid NOT NULL,
  comment_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_comment_likes_pkey PRIMARY KEY (user_id, comment_id),
  CONSTRAINT user_comment_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT user_comment_likes_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.news_comments(id)
);
CREATE TABLE public.user_fcm_tokens (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  token text NOT NULL,
  device_type text,
  last_used timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_fcm_tokens_pkey PRIMARY KEY (id),
  CONSTRAINT user_fcm_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.user_relationships (
  follower_id uuid NOT NULL,
  following_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_relationships_pkey PRIMARY KEY (follower_id, following_id),
  CONSTRAINT user_relationships_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public.nexususers(id),
  CONSTRAINT user_relationships_following_id_fkey FOREIGN KEY (following_id) REFERENCES public.nexususers(id)
);
CREATE TABLE public.verification_requirements (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  data_name text NOT NULL UNIQUE,
  badge_label text NOT NULL,
  input_type text NOT NULL,
  tier text DEFAULT 'Bronze'::text,
  is_global boolean DEFAULT false,
  description text,
  tag ARRAY,
  CONSTRAINT verification_requirements_pkey PRIMARY KEY (id)
);
CREATE TABLE public.verification_submissions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  requirement_id text,
  submitted_value text,
  submitted_at timestamp with time zone DEFAULT now(),
  status text DEFAULT 'pending'::text,
  rejection_reason text,
  CONSTRAINT verification_submissions_pkey PRIMARY KEY (id),
  CONSTRAINT verification_submissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.wishlists (
  user_id uuid NOT NULL,
  product_id uuid NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT wishlists_pkey PRIMARY KEY (user_id, product_id),
  CONSTRAINT wishlists_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.nexususers(id)
);