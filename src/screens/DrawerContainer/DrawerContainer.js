import React from "react";
import { View } from "react-native";
import PropTypes from "prop-types";
import styles from "./styles";
import MenuButton from "../../components/MenuButton/MenuButton";
import homeIcon from "../../../assets/icons/home.png";
import categoryIcon from "../../../assets/icons/category.png";
import searchIcon from "../../../assets/icons/search.png";

export default function DrawerContainer(props) {
  const { navigation } = props;
  return (
    <View style={styles.content}>
      <View style={styles.container}>
        <MenuButton
          title="HOME"
          source={homeIcon}
          onPress={() => {
            navigation.navigate("Main", { screen: "Home" });
            navigation.closeDrawer();
          }}
        />
        <MenuButton
          title="CATEGORIES"
          source={categoryIcon}
          onPress={() => {
            navigation.navigate("Main", { screen: "Categories" });
            navigation.closeDrawer();
          }}
        />
        <MenuButton
          title="SEARCH"
          source={searchIcon}
          onPress={() => {
            navigation.navigate("Main", { screen: "Search" });
            navigation.closeDrawer();
          }}
        />
      </View>
    </View>
  );
}

DrawerContainer.propTypes = {
  navigation: PropTypes.shape({
    navigate: PropTypes.func.isRequired,
    closeDrawer: PropTypes.func.isRequired,
  }).isRequired,
};

DrawerContainer.defaultProps = {
  navigation: {
    navigate: () => {},
    closeDrawer: () => {},
  },
};