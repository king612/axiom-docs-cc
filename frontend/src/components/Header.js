import React from 'react';
import { Container } from 'react-bootstrap';

// Logo from Axiom PLLC website
const LOGO_URL = 'https://axiompllc.com/wp-content/uploads/2021/08/Axiom-logo-color-2.png';

function Header() {
  return (
    <header className="bg-white py-2 mb-3 border-bottom">
      <Container className="text-center">
        <img
          src={LOGO_URL}
          alt="Axiom PLLC Logo"
          className="company-logo mb-1"
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
        <h1 className="header-title">Intelligent Proposal Assistant</h1>
      </Container>
    </header>
  );
}

export default Header;
