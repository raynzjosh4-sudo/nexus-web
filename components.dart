
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
