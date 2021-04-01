import React from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route,
} from "react-router-dom";

import Header from './components/header';
import Main from './pages/main';
import Map from './pages/map';
import Contact from './pages/contact';
import HowToBuy from './pages/how_to_buy';
import Profile from './pages/profile';

export default class App extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <Header />

                <Switch>
                    <Route exact path="/">
                        <Main />
                    </Route>
                    <Route path="/map">
                        <Map />
                    </Route>
                    <Route path="/how_to_buy">
                        <HowToBuy />
                    </Route>
                    <Route path="/contact">
                        <Contact />
                    </Route>
                    <Route path="/profile">
                        <Profile />
                    </Route>
                </Switch>
            </Router>
        );
    }
}