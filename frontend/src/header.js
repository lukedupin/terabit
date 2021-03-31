import React from 'react';
import Util from './helpers/util';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

export default class Header extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    render() {
        return (
            <header className="site_header">
                <nav className="navbar navbar-expand-lg">
                    <a className="navbar-brand logo_txt" href="#">Terabit</a>
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
                                <a className="nav-link" href="index.html">View Properties</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link" href="#">How to Buy</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link" href="#">Contact</a>
                            </li>
                        </ul>
                        <ul className="navbar-nav ml-auto">
                            <li className="nav-item pr-0">
                                <a className="btn btn-ghost" href="profile.html">My Profile</a>
                            </li>
                        </ul>
                    </div>
                </nav>
            </header>
        );
    }
}
