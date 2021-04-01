import React from 'react';
import ReactDOM from 'react-dom';
import {
    BrowserRouter as Router,
    Switch,
    Route,
} from "react-router-dom";

import Main from './pages/main';
import Map from './pages/map';
import Contact from './pages/contact';
import HowToBuy from './pages/how_to_buy';
import Profile from './pages/profile';

class App extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <header className="site_header">
                    <nav className="navbar navbar-expand-lg">
                        <a className="navbar-brand logo_txt" href="#" onClick={this.props.history.push('/')}>Terabit</a>
                        <button
                            className="navbar-toggler"
                            type="button"
                            data-toggle="collapse"
                            data-target="#navbarSupportedContent"
                            aria-controls="navbarSupportedContent"
                            aria-expanded="false"
                            aria-label="Toggle navigation"
                            onClick={this.props.history.push('/')}>
                            <span className="navbar-toggler-icon"></span>
                        </button>
                        <div className="collapse navbar-collapse" id="navbarSupportedContent">
                            <ul className="navbar-nav mr-auto">
                                <li className="nav-item active">
                                    <a className="nav-link" href="#" onClick={this.props.history.push('/map')}>View Properties</a>
                                </li>
                                <li className="nav-item">
                                    <a className="nav-link" href="#" onClick={this.props.history.push('/how_to_buy')}>How to Buy</a>
                                </li>
                                <li className="nav-item">
                                    <a className="nav-link" href="#" onClick={this.props.history.push('/contact')}>Contact</a>
                                </li>
                            </ul>
                            <ul className="navbar-nav ml-auto">
                                <li className="nav-item pr-0">
                                    <a className="btn btn-ghost" href="#" onClick={this.props.history.push('/profile')}>My Profile</a>
                                </li>
                            </ul>
                        </div>
                    </nav>
                </header>

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

ReactDOM.render(<App />, document.getElementById('app'));
