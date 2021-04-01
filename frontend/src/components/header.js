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

        this.state = {
            collapsed: true
        };

        this.toggleNav = this.toggleNav.bind(this)
        this.collapseNav = this.collapseNav.bind(this)
    }

    collapseNav( collapsed ) {
        this.setState({ collapsed })
    }

    toggleNav() {
        const collapsed = !this.state.collapsed
        this.setState({ collapsed })
    }

    isActive( test ) {
        return (test == window.location.pathname)? "active": ""
    }

    render() {
        //Is the nav collapsed?
        const collapsed_klass = (this.state.collapsed)? "collapse": "";

        return (
            <header className="site_header">
                <nav className="navbar navbar-expand-lg">
                    <Link className="navbar-brand logo_txt" to={'/'} onClick={this.collapseNav}>Terabit</Link>
                    <button
                        className="navbar-toggler"
                        type="button"
                        onClick={this.toggleNav}>
                        <span className="navbar-toggler-icon">HERE?</span>
                    </button>
                    <div className={collapsed_klass + " navbar-collapse"}>
                        <ul className="navbar-nav mr-auto">
                            <li className={"nav-item "+ this.isActive('/map')} onClick={this.collapseNav}>
                                <Link className="nav-link" to={'/map'}>View Properties</Link>
                            </li>
                            <li className={"nav-item "+ this.isActive('/how_to_buy')} onClick={this.collapseNav}>
                                <Link className="nav-link" to={'/how_to_buy'}>How to Buy</Link>
                            </li>
                            <li className={"nav-item "+ this.isActive('/contact')} onClick={this.collapseNav}>
                                <Link className="nav-link" to={'/contact'}>Contact</Link>
                            </li>
                        </ul>
                        <ul className="navbar-nav ml-auto">
                            <li className="nav-item pr-0" onClick={this.collapseNav}>
                                <Link className="btn btn-ghost" to={'/profile'}>My Profile</Link>
                            </li>
                        </ul>
                    </div>
                </nav>
            </header>
        );
    }
}