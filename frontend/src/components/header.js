import React from 'react';
import ReactDOM from 'react-dom';
import {Modal, Button} from 'react-bootstrap';
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
            collapsed: true,
            show_get_started: false,
            reload_required: false,
        };

        this.toggleNav = this.toggleNav.bind(this)
        this.collapseNav = this.collapseNav.bind(this)
        this.handleCloseModal = this.handleCloseModal.bind(this)
        this.handleOpenModal = this.handleOpenModal.bind(this)
        this.handleGetMetaMask = this.handleGetMetaMask.bind(this)
        this.handleReload = this.handleReload.bind(this)

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

    handleOpenModal() {
        this.setState({show_get_started: true})
    }

    handleCloseModal() {
        this.setState({show_get_started: false})
    }

    handleGetMetaMask() {
        window.open("https://metamask.io/download", "_blank")
        this.setState({reload_required: true})
    }

    handleReload() {
        window.location.reload(true);
        this.setState({show_get_started: false})
    }

    render() {
        const { show_get_started, reload_required } = this.state;
        //Is the nav collapsed?
        const collapsed_klass = (this.state.collapsed)? "collapse": "";

        const has_meta_mask = (typeof window.ethereum !== 'undefined');

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
                                {(has_meta_mask)? <Link className="btn btn-ghost" to={'/profile'}>My Profile</Link>:
                                                  <a className="btn btn-ghost" onClick={this.handleOpenModal}>Get started</a>}
                            </li>
                        </ul>
                    </div>
                </nav>

                { !has_meta_mask &&
                    <Modal show={show_get_started} onHide={this.handleCloseModal}>
                        <Modal.Header closeButton>
                            <Modal.Title>Get Started</Modal.Title>
                        </Modal.Header>
                        { (!reload_required)? <Modal.Body>Please install the Metamask plugin before attempting to view your profile.</Modal.Body>:
                                              <Modal.Body>Reloading the page is required for MetaMask changes to take effect.</Modal.Body>}
                        <Modal.Footer>
                            <Button variant="secondary" onClick={this.handleCloseModal}>
                                Close
                            </Button>
                            { (!reload_required)? <Button variant="primary" onClick={this.handleGetMetaMask}>Get MetaMask</Button>:
                                                  <Button variant="primary" onClick={this.handleReload}>Reload page</Button>}

                        </Modal.Footer>
                    </Modal>
                }
            </header>
        );
    }
}