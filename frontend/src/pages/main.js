import React from 'react';
import { Link } from "react-router-dom";

export default class Main extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <section id="hero">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-6 hero-text">
                                <div className="row">
                                    <div className="col-lg-6 offset-lg-3">
                                        <span className="pre-head">Patent-Pending</span>
                                        <h1>NFT the world.</h1>
                                        <hr/>
                                            <p>Buy and sell authentic NFT-registered land. Stake your claim, showcase NFTs, or develop software on the Teraverse coordinate platform.</p>
                                            <Link className="btn btn-ghost" to={'/map'}>View Properties</Link>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6 hero-img"></div>
                        </div>
                    </div>
                </section>

                <section id="manifest">
                    <div className="container-fluid">
                        <div className="row manifest">
                            <div className="col-lg-10 offset-lg-1">
                                <h2 className="h2-skinny">Today’s land may
                                    belong to the oligarchs and governments, but
                                    the next earth can belong to us. </h2>
                            </div>
                        </div>
                    </div>
                </section>

                <section id="benefits">
                    <div className="container-fluid">
                        <div className="row benefits-row-one">
                            <div className="col-lg-4 offset-lg-1">
                                <h3>Acquire new land</h3>
                                <p>Buy and sell kilometers of nft land. Units can be broken down to meters. Set resale prices or auction off at OpenSea.</p>
                            </div>
                            <div className="col-lg-4 offset-lg-2">
                                <h3>Showcase NFTs</h3>
                                <p>The value of an NFT comes from it’s environment and context. Create new value for NFTs by storing them where they are unique and can be experienced they way they should be.</p>
                            </div>
                        </div>
                        <div className="row benefits-row-two">
                            <div className="col-lg-4 offset-lg-1">
                                <h3>Tell a story</h3>
                                <p>Leave a legacy. Write your childhood story. Or a book. Or your update for today. It’s your land––write what you want on it.</p>
                            </div>
                            <div className="col-lg-4 offset-lg-2">
                                <h3>Develop the land</h3>
                                <p>Terabit is a base-level coordinate platform for software development. Build anything from communities to immersive reality using the Teraverse Development Platform.</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section id="function">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-6 function-img"></div>
                            <div className="col-lg-6 function-text">
                                <div className="row">
                                    <div className="col-lg-6 offset-lg-3">
                                        <span className="pre-head">Patent-Pending</span>
                                        <h2>Kilometer plots of land registered as authentic NFTs on the blockchain.</h2>
                                        <hr className="reverse"/>
                                            <p>We’ve broken apart the entire world based on lat/long, and created smart contracts for each parcel.</p>
                                            <p>Follow the Terabit Twitter to learn about new land grabs as they become available.</p>
                                            <a className="twitter-icon-button" href="https://twitter.com/get_terabit" target="_blank">
                                                <img src="images/icon-twitter.png" width="49" height="40" alt="Follow Terabit Twitter" />
                                            </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                <section id="deliverable">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-10 offset-lg-1">
                                <h2 className="h2-skinny">Buy Terabit. Here’s what you get.</h2>
                            </div>
                        </div>
                        <div className="row deliverable-row-one">
                            <div className="col-lg-4 offset-lg-1">
                                <h3>Aquire new land</h3>
                                <p>Buy and sell kilometers of nft land. Units can be broken down to meters. Set resale prices or auction off at OpenSea.</p>
                            </div>
                            <div className="col-lg-4 offset-lg-2">
                                <h3>Showcase NFTs</h3>
                                <p>The value of an NFT comes from it’s environment and context. Create new value for NFTs by storing them where they are unique and can be experienced they way they should be.</p>
                            </div>
                        </div>
                        <div className="row deliverable-row-two">
                            <div className="col-lg-4 offset-lg-1">
                                <h3>Tell a story</h3>
                                <p>Leave a legacy. Write your childhood story. Or a book. Or your update for today. It’s your land––write what you want on it.</p>
                            </div>
                            <div className="col-lg-4 offset-lg-2">
                                <h3>Develop the land</h3>
                                <p>Terabit is a base-level coordinate platform for software development. Build anything from communities to immersive reality using Teraverse Development Platform.</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section id="howtobuy">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-6 howtobuy-text">
                                <div className="row">
                                    <div className="col-lg-6 offset-lg-3">
                                        <h2>How to buy.</h2>
                                        <hr className="reverse"/>
                                        <dl>
                                            <dt>Step 1</dt>
                                            <dd>View Terabit Properties (coming this week).</dd>
                                            <dt>Step 2</dt>
                                            <dd>Setup a <a href="https://metamask.io/" target="_blank">MetaMask</a> crypto wallet.</dd>
                                            <dt>Step 3</dt>
                                            <dd>Find the Terabit listing on OpenSea, and buy using ETH or BTC from your MetaMask wallet.</dd>
                                            <dt>Step 4</dt>
                                            <dd>Checkout your new Terabit property.</dd>
                                        </dl>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6 howtobuy-img"></div>
                        </div>
                    </div>
                </section>

                <section id="developers">
                    <div className="container-fluid">
                        <div className="row developers">
                            <div className="col-lg-6 developers-text">
                                <div className="row">
                                    <div className="col-lg-6 offset-lg-3">
                                        <h2 className="h2-skinny">For Developers</h2>
                                        <p><strong>Terabit NFTs are the new domain.</strong> Beyond acting as a store of value, each Terabit has a registered URI that can be developed upon.</p>
                                        <p>Using the Teraverse API (currently in development), you can lay the new foundations of immersive reality, and other software applications.</p>
                                        <p>When you purchase a Terabit, you gain access the Teraverse Development Platform.</p>
                                       <a className="btn btn-ghost" href="https://discord.gg/Cj75nDpG" target="_blank">Join the Discord</a>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6 developers-img">
                                <img src="/static/images/mkt-devglobe.png" width="500" height="500" alt="Develop the world"/>
                            </div>
                        </div>
                    </div>
                </section>

                <section id="dudes">
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-lg-6 dudes-text">
                                <div className="row">
                                    <div className="col-lg-6 offset-lg-3">
                                        <h2>Who would do this?</h2>
                                        <hr className="reverse"/>
                                            <p>A couple of crypto rednecks from Idaho: Co-founders Ricky Lyman and Luke Dupin.</p>
                                            <p>We believe NFTs are the future. We love the incredible creativity and ingenuity coming out of the NFT revolution. But something is missing. When I can go see Jack Dorsey’s first tweet in a million places online, what makes it so valuable?</p>
                                            <p>In Terabit, there is only one first tweet. Your NFT exists only once. The value of an NFT ultimately comes from it’s environment and context. Terabit is that environment. It’s the tie between physical reality and the blockchain.</p>
                                            <p>Join us in charting out the new world ahead. For inquiries, please contact <a href="mailto:hello@get_terabit.com" target="_blank">hello@get_terabit.com</a>.</p>
                                    </div>
                                </div>
                            </div>
                            <div className="col-lg-6 dudes-img"></div>
                        </div>
                    </div>
                </section>
            </div>
        );
    }
}
