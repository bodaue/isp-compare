import React from 'react';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.footerContent}>
                <p>© 2025 ISP Compare | Керимов Тимур Илгарович | ВКР ПРИН-467</p>
            </div>
        </footer>
    );
};

export default Footer;