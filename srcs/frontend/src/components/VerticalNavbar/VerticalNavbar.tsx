"use client";

import React from "react";
import classes from './VerticalNavbar.module.css';
import Image from "next/image";
import mainLogo from '../../../assets/Main-Logo.svg';
import chatLogoWithe from '../../../assets/chatLogoWithe.svg';
import chatLogoBlack from '../../../assets/chatLogoBlack.svg';
import gameLogoWithe from '../../../assets/gameLogoWhite.svg';
import gameLogoBlack from '../../../assets/gameLogoBlack.svg';
import homeLogoWithe from '../../../assets/homeLogoWithe.svg';
import homeLogoBlack from '../../../assets/homeLogoBlack.svg';
import leaderboardWithe from '../../../assets/leaderboardWithe.svg';
import leaderboardBlack from '../../../assets/leaderboardBlack.svg';
import SettingsWithe from '../../../assets/SettingsWithe.svg';
import SettingsBlack from '../../../assets/SettingsBlack.svg';
import LogoutWithe from '../../../assets/LogoutWithe.svg';
import LogoutBlack from '../../../assets/LogoutBlack.svg';
import { useUserContext } from "../../context/UserContext";
import Link from "next/link";

const VerticalNavbar = () => {
    const pages = [
        { name: "home", logoBlack: homeLogoBlack, logoWhite: homeLogoWithe },
        { name: "chat", logoBlack: chatLogoBlack, logoWhite: chatLogoWithe },
        { name: "game", logoBlack: gameLogoBlack, logoWhite: gameLogoWithe },
        { name: "leaderboard", logoBlack: leaderboardBlack, logoWhite: leaderboardWithe },
        { name: "settings", logoBlack: SettingsBlack, logoWhite: SettingsWithe },
        { name: "logout", logoBlack: LogoutBlack, logoWhite: LogoutWithe }
    ];

    const { currentPage, updateCurrentPage } = useUserContext();

    const handlePageChange = (page: string) => {
        updateCurrentPage(page);
    };

    return (
        <nav className={classes.navbar}>
            <div className={classes.logo}>
                <Image className={classes.image} src={mainLogo} alt="Main Logo" />
            </div>
            <div className={classes.pagesButtons}>
                {pages.slice(0, 4).map((item) => (
                    <Link href={"/users/" + item.name} key={item.name}>
                        <button
                            className={item.name === currentPage ? classes.buttonSelected : classes.button}
                            onClick={() => handlePageChange(item.name)}
                        >
                            <Image 
                                className={classes.buttonImage} 
                                src={item.name === currentPage ? item.logoWhite : item.logoBlack} 
                                alt={item.name} 
                            />
                        </button>
                    </Link>
                ))}
            </div>
            <div className={classes.settingsAndLogout}>
                {pages.slice(4).map((item) => (
                    <Link href={"/users/" + item.name} key={item.name}>
                        <button
                            className={item.name === currentPage ? classes.buttonSelected : classes.button}
                            onClick={() => handlePageChange(item.name)}
                        >
                            <Image 
                                className={classes.buttonImage} 
                                src={item.name === currentPage ? item.logoWhite : item.logoBlack} 
                                alt={item.name} 
                            />
                        </button>
                    </Link>
                ))}
            </div>
        </nav>
    );
};

export default VerticalNavbar;