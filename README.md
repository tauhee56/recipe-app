# 🍳 Recipe App - React Native

A beautiful and intuitive recipe discovery app built with React Native and Expo. Discover delicious recipes, explore ingredients, and organize your favorite dishes all in one place.

## 📱 Features

- **Recipe Discovery**: Browse through a wide variety of recipes with beautiful images
- **Category Filtering**: Explore recipes by categories (Breakfast, Lunch, Dinner, Desserts, etc.)
- **Ingredient Search**: Find recipes based on available ingredients
- **Detailed Recipe View**: Step-by-step cooking instructions with ingredient lists
- **Ingredient Information**: Learn about different ingredients and their uses
- **Search Functionality**: Quick search to find your favorite recipes
- **Drawer Navigation**: Easy navigation with a clean sidebar menu
- **Responsive Design**: Optimized for both iOS and Android devices

## 🚀 Tech Stack

- **Framework**: React Native 0.76.6
- **Platform**: Expo ~52.0.25
- **Navigation**: React Navigation 7.0.0 (Stack & Drawer)
- **Language**: JavaScript/TypeScript
- **Animations**: React Native Reanimated 3.16.1
- **Image Handling**: React Native Fast Image
- **Carousel**: React Native Reanimated Carousel

## 📦 Installation

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Expo CLI
- Android Studio (for Android development)
- Xcode (for iOS development - macOS only)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/tauhee56/recipe-app.git
   cd recipe-app
   ```

2. **Install dependencies**
   ```bash
   # Using npm
   npm install
   
   # Using yarn
   yarn install
   ```

3. **Start the development server**
   ```bash
   # Using npm
   npm start
   
   # Using yarn
   yarn start
   ```

4. **Run on specific platforms**
   ```bash
   # Android
   npm run android
   # or
   yarn android
   
   # iOS
   npm run ios
   # or
   yarn ios
   
   # Web
   npm run web
   # or
   yarn web
   ```

## 📱 Screenshots

*Screenshots will be added soon*

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── BackButton/
│   ├── MenuButton/
│   ├── MenuImage/
│   └── ViewIngredientsButton/
├── data/               # Mock data and API
│   ├── MockDataAPI.js
│   └── dataArrays.js
├── navigations/        # Navigation configuration
│   └── AppNavigation.js
├── screens/            # App screens
│   ├── Categories/
│   ├── Details/
│   ├── DrawerContainer/
│   ├── Home/
│   ├── Ingredient/
│   ├── IngredientsDetails/
│   ├── LoadingScreen/
│   ├── Recipe/
│   ├── RecipesList/
│   ├── Search/
│   └── Splash/
└── AppStyles.js        # Global styles
```

## 🎨 Key Screens

- **Home Screen**: Featured recipes and categories overview
- **Categories Screen**: Browse recipes by food categories
- **Recipe Details**: Complete recipe with ingredients and instructions
- **Search Screen**: Find recipes by name or ingredients
- **Ingredients Screen**: Explore individual ingredients
- **Drawer Navigation**: Easy access to all app sections

## 🔧 Configuration

The app uses Expo configuration in `app.json`. Key configurations include:
- App name and version
- Platform-specific settings
- Asset and icon configurations
- Splash screen setup

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Tauhee**
- GitHub: [@tauhee56](https://github.com/tauhee56)

## 🙏 Acknowledgments

- Thanks to the React Native and Expo communities
- Recipe data and inspiration from various cooking websites
- Icons and images from various free resources

## 📞 Support

If you have any questions or need help with setup, please open an issue on GitHub.

---

**Happy Cooking! 🍽️**
