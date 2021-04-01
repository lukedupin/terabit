import React from 'react';
import ReactDOM from 'react-dom';
import { Link } from "react-router-dom";

import Main from '../pages/main';
import Map from '../pages/map';
import Contact from '../pages/contact';
import HowToBuy from '../pages/how_to_buy';
import Profile from '../pages/profile';

export default class App extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <header className="site_header">
                <nav className="navbar navbar-expand-lg">
                    <Link className="navbar-brand logo_txt" to={'/'}>Terabit</Link>
                    <button
                        className="navbar-toggler"
                        type="button"
                        data-toggle="collapse"
                        data-target="#navbarSupportedContent"
                        aria-controls="navbarSupportedContent"
                        aria-expanded="false"
                        aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarSupportedContent">
                        <ul className="navbar-nav mr-auto">
                            <li className="nav-item active">
                                <Link className="nav-link" to={'/map'}>View Properties</Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link" to={'/how_to_buy'}>How to Buy</Link>
                            </li>
                            <li className="nav-item">
                                <Link className="nav-link" to={'/contact'}>Contact</Link>
                            </li>
                        </ul>
                        <ul className="navbar-nav ml-auto">
                            <li className="nav-item pr-0">
                                <Link className="btn btn-ghost" to={'/profile'}>My Profile</Link>
                            </li>
                        </ul>
                    </div>
                </nav>
            </header>
        );
    }
}