import React, { lazy, Suspense } from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import DrawerContainer from '../screens/DrawerContainer/DrawerContainer';
import LoadingScreen from '../screens/LoadingScreen/LoadingScreen';

const HomeScreen = lazy(() => import('../screens/Home/HomeScreen'));
const CategoriesScreen = lazy(() => import('../screens/Categories/CategoriesScreen'));
const RecipeScreen = lazy(() => import('../screens/Recipe/RecipeScreen'));
const RecipesListScreen = lazy(() => import('../screens/RecipesList/RecipesListScreen'));
const IngredientScreen = lazy(() => import('../screens/Ingredient/IngredientScreen'));
const SearchScreen = lazy(() => import('../screens/Search/SearchScreen'));
const IngredientsDetailsScreen = lazy(() => import('../screens/IngredientsDetails/IngredientsDetailsScreen'));
const DetailsScreen = lazy(() => import('../screens/Details/DetailsScreen'));

const Stack = createStackNavigator();

function MainNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        headerTitleAlign: 'center',
      }}
    >
      <Stack.Screen name='Home' component={HomeScreen} />
      <Stack.Screen name='Categories' component={CategoriesScreen}/>
      <Stack.Screen name='Recipe' component={RecipeScreen}/>
      <Stack.Screen name='RecipesList' component={RecipesListScreen} />
      <Stack.Screen name='Ingredient' component={IngredientScreen} />
      <Stack.Screen name='Search' component={SearchScreen} />
      <Stack.Screen name='IngredientsDetails' component={IngredientsDetailsScreen} />
      <Stack.Screen name='Details' component={DetailsScreen} />
    </Stack.Navigator>
  );
}

const Drawer = createDrawerNavigator();

function DrawerStack() {
  return (
    <Drawer.Navigator
      screenOptions={{
        headerShown: false,
        drawerStyle: {
          width: 250, 
        },
      }}
      drawerContent={({navigation}) => <DrawerContainer navigation={navigation}/>}
    >
      <Drawer.Screen name='Main' component={MainNavigator} />
    </Drawer.Navigator>
  );
}

export default function AppContainer() {
  return (
    <NavigationContainer>
      <Suspense fallback={<LoadingScreen />}>
        <DrawerStack/>
      </Suspense>
    </NavigationContainer>
  );
}

console.disableYellowBox = true;