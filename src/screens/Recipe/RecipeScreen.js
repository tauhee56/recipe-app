import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import FastImage from 'react-native-fast-image';

const RecipeScreen = React.memo(({ route, navigation }) => {
  const { item } = route.params;
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, []);

  const renderIngredient = useCallback(({ item, index }) => (
    <Text key={index} style={styles.ingredient}>
      {item[1]} {item[0]}
    </Text>
  ), []);

  const renderStep = useCallback(({ item, index }) => (
    <Text key={index} style={styles.step}>
      {index + 1}. {item}
    </Text>
  ), []);

  return (
    <View style={styles.container}>
      <FastImage
        style={styles.headerImage}
        source={{
          uri: item.photo_url,
          priority: FastImage.priority.high,
        }}
        resizeMode={FastImage.resizeMode.cover}
        onLoadEnd={() => setLoading(false)}
      />
      {loading && <ActivityIndicator size="large" color="#ff6347" style={styles.loader} />}
      <View style={styles.contentContainer}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.category}>{item.category}</Text>
        <Text style={styles.description}>{item.description}</Text>

        <Text style={styles.sectionTitle}>Ingredients</Text>
        <FlatList
          data={item.ingredients}
          renderItem={renderIngredient}
          keyExtractor={(item, index) => `${item[0]}_${index}`}
        />

        <Text style={styles.sectionTitle}>Preparation Steps</Text>
        <FlatList
          data={item.steps}
          renderItem={renderStep}
          keyExtractor={(item, index) => `${index}`}
        />

        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.navigate('IngredientsDetails', { ingredients: item.ingredients })}
        >
          <Text style={styles.buttonText}>View Ingredients</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
});

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  headerImage: {
    width: '100%',
    height: 250,
  },
  loader: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: [{ translateX: -25 }, { translateY: -25 }],
  },
  contentContainer: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  category: {
    fontSize: 18,
    color: '#888',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    lineHeight: 22,
    color: '#666',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  ingredient: {
    fontSize: 16,
    color: '#555',
    marginBottom: 5,
  },
  step: {
    fontSize: 16,
    color: '#555',
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#ff6347', // Tomato color
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default RecipeScreen;
