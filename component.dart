import 'package:equatable/equatable.dart';

// --- 1. THE BASE CLASS ---
abstract class ProfileComponent extends Equatable {
  const ProfileComponent();

  @override
  List<Object?> get props => [];

  // Convert object to JSON for Supabase
  Map<String, dynamic> toJson();

  // Convert JSON from Supabase back to object
  factory ProfileComponent.fromJson(Map<String, dynamic> json) {
    final type = json['type'] as String?;
    switch (type) {
      case 'ProfileHeroComponent':
        return ProfileHeroComponent.fromJson(json);
      case 'ProfileGalleryComponent':
        return ProfileGalleryComponent.fromJson(json);
      case 'ProfileVideoComponent':
        return ProfileVideoComponent.fromJson(json);
      case 'ProfileMapComponent':
        return ProfileMapComponent.fromJson(json);
      case 'ProfileHeadingComponent':
        return ProfileHeadingComponent.fromJson(json);
      case 'ProfileBioComponent':
        return ProfileBioComponent.fromJson(json);
      case 'ProfileContactComponent':
        return ProfileContactComponent.fromJson(json);
      case 'ProfileTestimonialComponent':
        return ProfileTestimonialComponent.fromJson(json);
      case 'ProfileCtaComponent':
        return ProfileCtaComponent.fromJson(json);
      case 'ProfilePricingComponent':
        return ProfilePricingComponent.fromJson(json);
      case 'ProfileFaqComponent':
        return ProfileFaqComponent.fromJson(json);
      case 'ProfileFeatureListComponent':
        return ProfileFeatureListComponent.fromJson(json);
      case 'ProfileTeamComponent':
        return ProfileTeamComponent.fromJson(json);
      case 'ProfileTimelineComponent':
        return ProfileTimelineComponent.fromJson(json);
      case 'ProfileFileDownloadComponent':
        return ProfileFileDownloadComponent.fromJson(json);
      case 'ProfileDividerComponent':
        return ProfileDividerComponent.fromJson(json);
      case 'ProfilePortfolioComponent':
        return ProfilePortfolioComponent.fromJson(json);
      case 'ProfileServiceListComponent':
        return ProfileServiceListComponent.fromJson(json);
      case 'ProfileBookingComponent':
        return ProfileBookingComponent.fromJson(json);
      case 'ProfileAwardsComponent':
        return ProfileAwardsComponent.fromJson(json);
      case 'ProfileTabbedContentComponent':
        return ProfileTabbedContentComponent.fromJson(json);
      case 'ProfileFeedComponent':
        return ProfileFeedComponent.fromJson(json);
      case 'ProfileWebsiteThemeComponent':
        return ProfileWebsiteThemeComponent.fromJson(json);
      default:
        // Fallback for unknown types or empty component slots
        // In production, you might want to return a dummy empty component
        // or throw an error. For now, we throw to help debugging.
        throw UnimplementedError('Unknown component type: $type');
    }
  }
}

// --- 2. HERO COMPONENT ---
enum HeroStyle { textOverlay, textBelow, splitLeft, splitRight }

class ProfileHeroComponent extends ProfileComponent {
  final String title;
  final String? subtitle;
  final String imageUrl;
  final HeroStyle style;

  const ProfileHeroComponent({
    required this.title,
    this.subtitle,
    required this.imageUrl,
    this.style = HeroStyle.textOverlay,
  });

  @override
  List<Object?> get props => [title, subtitle, imageUrl, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileHeroComponent',
        'title': title,
        'subtitle': subtitle,
        'imageUrl': imageUrl,
        'style': style.name,
      };

  factory ProfileHeroComponent.fromJson(Map<String, dynamic> json) =>
      ProfileHeroComponent(
        title: json['title'],
        subtitle: json['subtitle'],
        imageUrl: json['imageUrl'],
        style: HeroStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => HeroStyle.textOverlay,
        ),
      );

  /// Returns a copy of this component with fields replaced by provided values.
  ProfileHeroComponent copyWith({
    String? title,
    String? subtitle,
    String? imageUrl,
    HeroStyle? style,
  }) {
    return ProfileHeroComponent(
      title: title ?? this.title,
      subtitle: subtitle ?? this.subtitle,
      imageUrl: imageUrl ?? this.imageUrl,
      style: style ?? this.style,
    );
  }
}

// --- 3. GALLERY COMPONENT ---
enum GalleryStyle { grid, carousel, masonry, filmstrip }

class ProfileGalleryComponent extends ProfileComponent {
  final List<String> imageUrls;
  final String? title;
  final GalleryStyle style;

  const ProfileGalleryComponent({
    required this.imageUrls,
    this.title,
    this.style = GalleryStyle.grid,
  });

  @override
  List<Object?> get props => [imageUrls, title, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileGalleryComponent',
        'imageUrls': imageUrls,
        'title': title,
        'style': style.name,
      };

  factory ProfileGalleryComponent.fromJson(Map<String, dynamic> json) =>
      ProfileGalleryComponent(
        imageUrls: List<String>.from(json['imageUrls'] ?? []),
        title: json['title'],
        style: GalleryStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => GalleryStyle.grid,
        ),
      );
}

// --- 4. VIDEO COMPONENT ---
enum VideoStyle { singlePlayer, playlist }

class ProfileVideoComponent extends ProfileComponent {
  final List<String> videoUrls;
  final String? title;
  final VideoStyle style;

  const ProfileVideoComponent({
    required this.videoUrls,
    this.title,
    this.style = VideoStyle.singlePlayer,
  });

  @override
  List<Object?> get props => [videoUrls, title, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileVideoComponent',
        'videoUrls': videoUrls,
        'title': title,
        'style': style.name,
      };

  factory ProfileVideoComponent.fromJson(Map<String, dynamic> json) =>
      ProfileVideoComponent(
        videoUrls: List<String>.from(json['videoUrls'] ?? []),
        title: json['title'],
        style: VideoStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => VideoStyle.singlePlayer,
        ),
      );
}

// --- 5. MAP & LOCATIONS COMPONENT ---
class MapLocation extends Equatable {
  final double latitude;
  final double longitude;
  final String title;
  final String? description;

  const MapLocation({
    required this.latitude,
    required this.longitude,
    required this.title,
    this.description,
  });

  @override
  List<Object?> get props => [latitude, longitude, title, description];

  Map<String, dynamic> toJson() => {
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'description': description,
      };

  factory MapLocation.fromJson(Map<String, dynamic> json) => MapLocation(
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        title: json['title'],
        description: json['description'],
      );
}

class ProfileMapComponent extends ProfileComponent {
  final List<MapLocation> locations;
  final String? title;

  const ProfileMapComponent({required this.locations, this.title});

  @override
  List<Object?> get props => [locations, title];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileMapComponent',
        'locations': locations.map((e) => e.toJson()).toList(),
        'title': title,
      };

  factory ProfileMapComponent.fromJson(Map<String, dynamic> json) =>
      ProfileMapComponent(
        locations: (json['locations'] as List)
            .map((e) => MapLocation.fromJson(e))
            .toList(),
        title: json['title'],
      );
}

// --- 6. TEXT & CONTENT COMPONENTS (Heading) ---
enum HeadingStyle { normal, leftAligned, centered }

class ProfileHeadingComponent extends ProfileComponent {
  final String text;
  final double size;
  final HeadingStyle style;
  final String? color;
  final bool animate;

  const ProfileHeadingComponent({
    required this.text,
    this.size = 1,
    this.style = HeadingStyle.normal,
    this.color,
    this.animate = false,
  });

  @override
  List<Object?> get props => [text, size, style, color, animate];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileHeadingComponent',
        'text': text,
        'size': size,
        'style': style.name,
        'color': color,
        'animate': animate,
      };

  factory ProfileHeadingComponent.fromJson(Map<String, dynamic> json) =>
      ProfileHeadingComponent(
        text: json['text'],
        size: (json['size'] as num).toDouble(),
        style: HeadingStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => HeadingStyle.normal,
        ),
        color: json['color'],
        animate: json['animate'] ?? false,
      );
}

// --- 6b. TEXT & CONTENT COMPONENTS (Bio) ---
enum ProfileBioAlignment { left, center, right, justify }

class ProfileBioComponent extends ProfileComponent {
  final String text;
  final bool showMoreEnabled;
  final ProfileBioAlignment alignment;
  final String? backgroundColor;
  final String? backgroundImageUrl;
  final String? textColor;

  const ProfileBioComponent({
    required this.text,
    this.showMoreEnabled = false,
    this.alignment = ProfileBioAlignment.left,
    this.backgroundColor,
    this.backgroundImageUrl,
    this.textColor,
  });

  @override
  List<Object?> get props => [
        text,
        showMoreEnabled,
        alignment,
        backgroundColor,
        backgroundImageUrl,
        textColor,
      ];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileBioComponent',
        'text': text,
        'showMoreEnabled': showMoreEnabled,
        'alignment': alignment.name,
        'backgroundColor': backgroundColor,
        'backgroundImageUrl': backgroundImageUrl,
        'textColor': textColor,
      };

  factory ProfileBioComponent.fromJson(Map<String, dynamic> json) =>
      ProfileBioComponent(
        text: json['text'],
        showMoreEnabled: json['showMoreEnabled'] ?? false,
        alignment: ProfileBioAlignment.values.firstWhere(
          (e) => e.name == json['alignment'],
          orElse: () => ProfileBioAlignment.left,
        ),
        backgroundColor: json['backgroundColor'],
        backgroundImageUrl: json['backgroundImageUrl'],
        textColor: json['textColor'],
      );
}

// --- 7. CONTACT COMPONENT ---
enum ContactStyle { simpleList, form }

class ProfileContactItem extends Equatable {
  final String name;
  final String? email;
  final String? phone;

  const ProfileContactItem({required this.name, this.email, this.phone});

  @override
  List<Object?> get props => [name, email, phone];

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
        'phone': phone,
      };

  factory ProfileContactItem.fromJson(Map<String, dynamic> json) =>
      ProfileContactItem(
        name: json['name'],
        email: json['email'],
        phone: json['phone'],
      );
}

class ProfileContactComponent extends ProfileComponent {
  final String title;
  final List<ProfileContactItem> contacts;
  final ContactStyle style;

  const ProfileContactComponent({
    required this.title,
    required this.contacts,
    this.style = ContactStyle.simpleList,
  });

  @override
  List<Object?> get props => [title, contacts, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileContactComponent',
        'title': title,
        'contacts': contacts.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfileContactComponent.fromJson(Map<String, dynamic> json) =>
      ProfileContactComponent(
        title: json['title'],
        contacts: (json['contacts'] as List)
            .map((e) => ProfileContactItem.fromJson(e))
            .toList(),
        style: ContactStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => ContactStyle.simpleList,
        ),
      );
}

// --- 8. TESTIMONIAL COMPONENT ---
enum TestimonialStyle { singleQuote, quoteList, quoteCarousel }

class ProfileTestimonialItem extends Equatable {
  final String quote;
  final String authorName;
  final String? authorTitle;
  final String? authorImageUrl;

  const ProfileTestimonialItem({
    required this.quote,
    required this.authorName,
    this.authorTitle,
    this.authorImageUrl,
  });

  @override
  List<Object?> get props => [quote, authorName, authorTitle, authorImageUrl];

  Map<String, dynamic> toJson() => {
        'quote': quote,
        'authorName': authorName,
        'authorTitle': authorTitle,
        'authorImageUrl': authorImageUrl,
      };

  factory ProfileTestimonialItem.fromJson(Map<String, dynamic> json) =>
      ProfileTestimonialItem(
        quote: json['quote'],
        authorName: json['authorName'],
        authorTitle: json['authorTitle'],
        authorImageUrl: json['authorImageUrl'],
      );
}

class ProfileTestimonialComponent extends ProfileComponent {
  final String? title;
  final List<ProfileTestimonialItem> testimonials;
  final TestimonialStyle style;

  const ProfileTestimonialComponent({
    this.title,
    required this.testimonials,
    this.style = TestimonialStyle.quoteList,
  });

  @override
  List<Object?> get props => [title, testimonials, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileTestimonialComponent',
        'title': title,
        'testimonials': testimonials.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfileTestimonialComponent.fromJson(Map<String, dynamic> json) =>
      ProfileTestimonialComponent(
        title: json['title'],
        testimonials: (json['testimonials'] as List)
            .map((e) => ProfileTestimonialItem.fromJson(e))
            .toList(),
        style: TestimonialStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => TestimonialStyle.quoteList,
        ),
      );
}

// --- 9. CALL TO ACTION (CTA) COMPONENT ---
enum CtaStyle { fullWidthButton, featuredBox }

class ProfileCtaComponent extends ProfileComponent {
  final String title;
  final String? subtitle;
  final String buttonText;
  final String actionUrl;
  final CtaStyle style;

  const ProfileCtaComponent({
    required this.title,
    this.subtitle,
    required this.buttonText,
    required this.actionUrl,
    this.style = CtaStyle.featuredBox,
  });

  @override
  List<Object?> get props => [title, subtitle, buttonText, actionUrl, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileCtaComponent',
        'title': title,
        'subtitle': subtitle,
        'buttonText': buttonText,
        'actionUrl': actionUrl,
        'style': style.name,
      };

  factory ProfileCtaComponent.fromJson(Map<String, dynamic> json) =>
      ProfileCtaComponent(
        title: json['title'],
        subtitle: json['subtitle'],
        buttonText: json['buttonText'],
        actionUrl: json['actionUrl'],
        style: CtaStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => CtaStyle.featuredBox,
        ),
      );
}

// --- 10. PRICING TABLE COMPONENT ---
enum PricingStyle { simpleList, featureGrid }

class PricingTierFeature extends Equatable {
  final String featureText;
  final bool isAvailable;

  const PricingTierFeature({
    required this.featureText,
    this.isAvailable = true,
  });

  @override
  List<Object?> get props => [featureText, isAvailable];

  Map<String, dynamic> toJson() => {
        'featureText': featureText,
        'isAvailable': isAvailable,
      };

  factory PricingTierFeature.fromJson(Map<String, dynamic> json) =>
      PricingTierFeature(
        featureText: json['featureText'],
        isAvailable: json['isAvailable'] ?? true,
      );
}

class PricingTier extends Equatable {
  final String title;
  final String price;
  final String perUnit;
  final List<PricingTierFeature> features;
  final bool isFeatured;

  const PricingTier({
    required this.title,
    required this.price,
    required this.perUnit,
    required this.features,
    this.isFeatured = false,
  });

  @override
  List<Object?> get props => [title, price, perUnit, features, isFeatured];

  Map<String, dynamic> toJson() => {
        'title': title,
        'price': price,
        'perUnit': perUnit,
        'features': features.map((e) => e.toJson()).toList(),
        'isFeatured': isFeatured,
      };

  factory PricingTier.fromJson(Map<String, dynamic> json) => PricingTier(
        title: json['title'],
        price: json['price'],
        perUnit: json['perUnit'],
        features: (json['features'] as List)
            .map((e) => PricingTierFeature.fromJson(e))
            .toList(),
        isFeatured: json['isFeatured'] ?? false,
      );
}

class ProfilePricingComponent extends ProfileComponent {
  final String? title;
  final List<PricingTier> tiers;
  final PricingStyle style;

  const ProfilePricingComponent({
    this.title,
    required this.tiers,
    this.style = PricingStyle.featureGrid,
  });

  @override
  List<Object?> get props => [title, tiers, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfilePricingComponent',
        'title': title,
        'tiers': tiers.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfilePricingComponent.fromJson(Map<String, dynamic> json) =>
      ProfilePricingComponent(
        title: json['title'],
        tiers: (json['tiers'] as List)
            .map((e) => PricingTier.fromJson(e))
            .toList(),
        style: PricingStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => PricingStyle.featureGrid,
        ),
      );
}

// --- 11. FAQ COMPONENT ---
class FaqItem extends Equatable {
  final String question;
  final String answer;

  const FaqItem({required this.question, required this.answer});

  @override
  List<Object?> get props => [question, answer];

  Map<String, dynamic> toJson() => {'question': question, 'answer': answer};

  factory FaqItem.fromJson(Map<String, dynamic> json) =>
      FaqItem(question: json['question'], answer: json['answer']);
}

class ProfileFaqComponent extends ProfileComponent {
  final String? title;
  final List<FaqItem> items;

  const ProfileFaqComponent({this.title, required this.items});

  @override
  List<Object?> get props => [title, items];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileFaqComponent',
        'title': title,
        'items': items.map((e) => e.toJson()).toList(),
      };

  factory ProfileFaqComponent.fromJson(Map<String, dynamic> json) =>
      ProfileFaqComponent(
        title: json['title'],
        items: (json['items'] as List).map((e) => FaqItem.fromJson(e)).toList(),
      );
}

// --- 12. FEATURE LIST COMPONENT ---
enum FeatureListStyle { iconLeft, iconTop }

class ProfileFeatureItem extends Equatable {
  final String icon;
  final String title;
  final String description;

  const ProfileFeatureItem({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  List<Object?> get props => [icon, title, description];

  Map<String, dynamic> toJson() => {
        'icon': icon,
        'title': title,
        'description': description,
      };

  factory ProfileFeatureItem.fromJson(Map<String, dynamic> json) =>
      ProfileFeatureItem(
        icon: json['icon'],
        title: json['title'],
        description: json['description'],
      );
}

class ProfileFeatureListComponent extends ProfileComponent {
  final String? title;
  final List<ProfileFeatureItem> features;
  final FeatureListStyle style;

  const ProfileFeatureListComponent({
    this.title,
    required this.features,
    this.style = FeatureListStyle.iconLeft,
  });

  @override
  List<Object?> get props => [title, features, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileFeatureListComponent',
        'title': title,
        'features': features.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfileFeatureListComponent.fromJson(Map<String, dynamic> json) =>
      ProfileFeatureListComponent(
        title: json['title'],
        features: (json['features'] as List)
            .map((e) => ProfileFeatureItem.fromJson(e))
            .toList(),
        style: FeatureListStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => FeatureListStyle.iconLeft,
        ),
      );
}

// --- 13. TEAM COMPONENT ---
enum TeamStyle { grid, list }

class ProfileTeamMember extends Equatable {
  final String name;
  final String title;
  final String? bio;
  final String imageUrl;

  const ProfileTeamMember({
    required this.name,
    required this.title,
    this.bio,
    required this.imageUrl,
  });

  @override
  List<Object?> get props => [name, title, bio, imageUrl];

  Map<String, dynamic> toJson() => {
        'name': name,
        'title': title,
        'bio': bio,
        'imageUrl': imageUrl,
      };

  factory ProfileTeamMember.fromJson(Map<String, dynamic> json) =>
      ProfileTeamMember(
        name: json['name'],
        title: json['title'],
        bio: json['bio'],
        imageUrl: json['imageUrl'],
      );
}

class ProfileTeamComponent extends ProfileComponent {
  final String? title;
  final List<ProfileTeamMember> members;
  final TeamStyle style;

  const ProfileTeamComponent({
    this.title,
    required this.members,
    this.style = TeamStyle.grid,
  });

  @override
  List<Object?> get props => [title, members, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileTeamComponent',
        'title': title,
        'members': members.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfileTeamComponent.fromJson(Map<String, dynamic> json) =>
      ProfileTeamComponent(
        title: json['title'],
        members: (json['members'] as List)
            .map((e) => ProfileTeamMember.fromJson(e))
            .toList(),
        style: TeamStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => TeamStyle.grid,
        ),
      );
}

// --- 14. TIMELINE COMPONENT ---
class ProfileTimelineItem extends Equatable {
  final String date;
  final String title;
  final String? description;

  const ProfileTimelineItem({
    required this.date,
    required this.title,
    this.description,
  });

  @override
  List<Object?> get props => [date, title, description];

  Map<String, dynamic> toJson() => {
        'date': date,
        'title': title,
        'description': description,
      };

  factory ProfileTimelineItem.fromJson(Map<String, dynamic> json) =>
      ProfileTimelineItem(
        date: json['date'],
        title: json['title'],
        description: json['description'],
      );
}

class ProfileTimelineComponent extends ProfileComponent {
  final String? title;
  final List<ProfileTimelineItem> items;

  const ProfileTimelineComponent({this.title, required this.items});

  @override
  List<Object?> get props => [title, items];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileTimelineComponent',
        'title': title,
        'items': items.map((e) => e.toJson()).toList(),
      };

  factory ProfileTimelineComponent.fromJson(Map<String, dynamic> json) =>
      ProfileTimelineComponent(
        title: json['title'],
        items: (json['items'] as List)
            .map((e) => ProfileTimelineItem.fromJson(e))
            .toList(),
      );
}

// --- 15. FILE DOWNLOAD COMPONENT ---
class ProfileFileDownloadItem extends Equatable {
  final String title;
  final String? description;
  final String fileUrl;
  final String fileType;
  final String? fileSize;

  const ProfileFileDownloadItem({
    required this.title,
    this.description,
    required this.fileUrl,
    required this.fileType,
    this.fileSize,
  });

  @override
  List<Object?> get props => [title, description, fileUrl, fileType, fileSize];

  Map<String, dynamic> toJson() => {
        'title': title,
        'description': description,
        'fileUrl': fileUrl,
        'fileType': fileType,
        'fileSize': fileSize,
      };

  factory ProfileFileDownloadItem.fromJson(Map<String, dynamic> json) =>
      ProfileFileDownloadItem(
        title: json['title'],
        description: json['description'],
        fileUrl: json['fileUrl'],
        fileType: json['fileType'],
        fileSize: json['fileSize'],
      );
}

class ProfileFileDownloadComponent extends ProfileComponent {
  final String? title;
  final List<ProfileFileDownloadItem> files;

  const ProfileFileDownloadComponent({this.title, required this.files});

  @override
  List<Object?> get props => [title, files];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileFileDownloadComponent',
        'title': title,
        'files': files.map((e) => e.toJson()).toList(),
      };

  factory ProfileFileDownloadComponent.fromJson(Map<String, dynamic> json) =>
      ProfileFileDownloadComponent(
        title: json['title'],
        files: (json['files'] as List)
            .map((e) => ProfileFileDownloadItem.fromJson(e))
            .toList(),
      );
}

// --- 16. DIVIDER COMPONENT ---
class ProfileDividerComponent extends ProfileComponent {
  const ProfileDividerComponent();

  @override
  Map<String, dynamic> toJson() => {'type': 'ProfileDividerComponent'};

  factory ProfileDividerComponent.fromJson(Map<String, dynamic> json) =>
      const ProfileDividerComponent();
}

// --- 17. PORTFOLIO COMPONENT ---
enum PortfolioStyle { grid, list, carousel, horizontalList }

class ProfilePortfolioItem extends Equatable {
  final String title;
  final String? description;
  final String imageUrl;
  final String? status;
  final String? projectUrl;

  const ProfilePortfolioItem({
    required this.title,
    this.description,
    required this.imageUrl,
    this.status,
    this.projectUrl,
  });

  @override
  List<Object?> get props => [title, description, imageUrl, status, projectUrl];

  Map<String, dynamic> toJson() => {
        'title': title,
        'description': description,
        'imageUrl': imageUrl,
        'status': status,
        'projectUrl': projectUrl,
      };

  factory ProfilePortfolioItem.fromJson(Map<String, dynamic> json) =>
      ProfilePortfolioItem(
        title: json['title'],
        description: json['description'],
        imageUrl: json['imageUrl'],
        status: json['status'],
        projectUrl: json['projectUrl'],
      );
}

class ProfilePortfolioComponent extends ProfileComponent {
  final String? title;
  final List<ProfilePortfolioItem> projects;
  final PortfolioStyle style;

  const ProfilePortfolioComponent({
    this.title,
    required this.projects,
    this.style = PortfolioStyle.grid,
  });

  @override
  List<Object?> get props => [title, projects, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfilePortfolioComponent',
        'title': title,
        'projects': projects.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfilePortfolioComponent.fromJson(Map<String, dynamic> json) =>
      ProfilePortfolioComponent(
        title: json['title'],
        projects: (json['projects'] as List)
            .map((e) => ProfilePortfolioItem.fromJson(e))
            .toList(),
        style: PortfolioStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => PortfolioStyle.grid,
        ),
      );
}

// --- 18. SERVICE LIST COMPONENT ---
enum ServiceListStyle { list, detailed }

class ProfileServiceItem extends Equatable {
  final String name;
  final String? description;
  final String? imageUrl;

  const ProfileServiceItem({
    required this.name,
    this.description,
    this.imageUrl,
  });

  @override
  List<Object?> get props => [name, description, imageUrl];

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'imageUrl': imageUrl,
      };

  factory ProfileServiceItem.fromJson(Map<String, dynamic> json) =>
      ProfileServiceItem(
        name: json['name'],
        description: json['description'],
        imageUrl: json['imageUrl'],
      );
}

class ProfileServiceListComponent extends ProfileComponent {
  final String? title;
  final List<ProfileServiceItem> services;
  final ServiceListStyle style;

  const ProfileServiceListComponent({
    this.title,
    required this.services,
    this.style = ServiceListStyle.list,
  });

  @override
  List<Object?> get props => [title, services, style];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileServiceListComponent',
        'title': title,
        'services': services.map((e) => e.toJson()).toList(),
        'style': style.name,
      };

  factory ProfileServiceListComponent.fromJson(Map<String, dynamic> json) =>
      ProfileServiceListComponent(
        title: json['title'],
        services: (json['services'] as List)
            .map((e) => ProfileServiceItem.fromJson(e))
            .toList(),
        style: ServiceListStyle.values.firstWhere(
          (e) => e.name == json['style'],
          orElse: () => ServiceListStyle.list,
        ),
      );
}

// --- 19. BOOKING COMPONENT ---
class ProfileBookingComponent extends ProfileComponent {
  final String title;
  final String? subtitle;
  final String buttonText;
  final String bookingUrl;

  const ProfileBookingComponent({
    required this.title,
    this.subtitle,
    this.buttonText = "Book an Appointment",
    required this.bookingUrl,
  });

  @override
  List<Object?> get props => [title, subtitle, buttonText, bookingUrl];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileBookingComponent',
        'title': title,
        'subtitle': subtitle,
        'buttonText': buttonText,
        'bookingUrl': bookingUrl,
      };

  factory ProfileBookingComponent.fromJson(Map<String, dynamic> json) =>
      ProfileBookingComponent(
        title: json['title'],
        subtitle: json['subtitle'],
        buttonText: json['buttonText'],
        bookingUrl: json['bookingUrl'],
      );
}

// --- 20. AWARDS & CERTIFICATIONS COMPONENT ---
class ProfileAwardItem extends Equatable {
  final String title;
  final String? issuer;
  final String? year;
  final String? imageUrl;

  const ProfileAwardItem({
    required this.title,
    this.issuer,
    this.year,
    this.imageUrl,
  });

  @override
  List<Object?> get props => [title, issuer, year, imageUrl];

  Map<String, dynamic> toJson() => {
        'title': title,
        'issuer': issuer,
        'year': year,
        'imageUrl': imageUrl,
      };

  factory ProfileAwardItem.fromJson(Map<String, dynamic> json) =>
      ProfileAwardItem(
        title: json['title'],
        issuer: json['issuer'],
        year: json['year'],
        imageUrl: json['imageUrl'],
      );
}

class ProfileAwardsComponent extends ProfileComponent {
  final String? title;
  final List<ProfileAwardItem> awards;

  const ProfileAwardsComponent({
    this.title = "Awards & Certifications",
    required this.awards,
  });

  @override
  List<Object?> get props => [title, awards];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileAwardsComponent',
        'title': title,
        'awards': awards.map((e) => e.toJson()).toList(),
      };

  factory ProfileAwardsComponent.fromJson(Map<String, dynamic> json) =>
      ProfileAwardsComponent(
        title: json['title'],
        awards: (json['awards'] as List)
            .map((e) => ProfileAwardItem.fromJson(e))
            .toList(),
      );
}

// --- 21. TABBED CONTENT COMPONENT ---
class ProfileTabItem extends Equatable {
  final String title;
  final List<ProfileComponent> components;

  const ProfileTabItem({required this.title, required this.components});

  @override
  List<Object?> get props => [title, components];

  Map<String, dynamic> toJson() => {
        'title': title,
        'components': components.map((e) => e.toJson()).toList(),
      };

  factory ProfileTabItem.fromJson(Map<String, dynamic> json) => ProfileTabItem(
        title: json['title'],
        // Recursively parse the components inside the tab
        components: (json['components'] as List)
            .map((e) => ProfileComponent.fromJson(e))
            .toList(),
      );
}

class ProfileTabbedContentComponent extends ProfileComponent {
  final List<ProfileTabItem> tabs;

  const ProfileTabbedContentComponent({required this.tabs});

  @override
  List<Object?> get props => [tabs];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileTabbedContentComponent',
        'tabs': tabs.map((e) => e.toJson()).toList(),
      };

  factory ProfileTabbedContentComponent.fromJson(Map<String, dynamic> json) =>
      ProfileTabbedContentComponent(
        tabs: (json['tabs'] as List)
            .map((e) => ProfileTabItem.fromJson(e))
            .toList(),
      );
}

// --- 22. FEED COMPONENT ---
class ProfileFeedComponent extends ProfileComponent {
  final String profileDomain;

  const ProfileFeedComponent({required this.profileDomain});

  @override
  List<Object?> get props => [profileDomain];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileFeedComponent',
        'profileDomain': profileDomain,
      };

  factory ProfileFeedComponent.fromJson(Map<String, dynamic> json) =>
      ProfileFeedComponent(profileDomain: json['profileDomain']);
}

// --- 23. WEBSITE THEME COMPONENT ---
class ProfileWebsiteThemeComponent extends ProfileComponent {
  final String primaryColor;
  final String secondaryColor;
  final String backgroundColor;
  final String surfaceColor;
  final String textColor;
  final String accentColor;

  const ProfileWebsiteThemeComponent({
    this.primaryColor = '#6200EE',
    this.secondaryColor = '#03DAC6',
    this.backgroundColor = '#F5F5F5',
    this.surfaceColor = '#FFFFFF',
    this.textColor = '#000000',
    this.accentColor = '#FF5722',
  });

  @override
  List<Object?> get props => [
        primaryColor,
        secondaryColor,
        backgroundColor,
        surfaceColor,
        textColor,
        accentColor,
      ];

  @override
  Map<String, dynamic> toJson() => {
        'type': 'ProfileWebsiteThemeComponent',
        'primaryColor': primaryColor,
        'secondaryColor': secondaryColor,
        'backgroundColor': backgroundColor,
        'surfaceColor': surfaceColor,
        'textColor': textColor,
        'accentColor': accentColor,
      };

  factory ProfileWebsiteThemeComponent.fromJson(Map<String, dynamic> json) =>
      ProfileWebsiteThemeComponent(
        primaryColor: json['primaryColor'] ?? '#6200EE',
        secondaryColor: json['secondaryColor'] ?? '#03DAC6',
        backgroundColor: json['backgroundColor'] ?? '#F5F5F5',
        surfaceColor: json['surfaceColor'] ?? '#FFFFFF',
        textColor: json['textColor'] ?? '#000000',
        accentColor: json['accentColor'] ?? '#FF5722',
      );
}
