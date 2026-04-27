// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

contract Airdrop {
    address public owner;
    address[] public donorsList; // Lista de todas las direcciones que han donado
    mapping(address => uint256) public donationAmount; // Cuánto ha donado cada uno

    event Donated(address indexed donor, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Función para recibir dinero (ETH) directamente. 
     * Se activa cuando alguien envía dinero al contrato.
     */
    receive() external payable {
        if (donationAmount[msg.sender] == 0) {
            donorsList.push(msg.sender);
        }
        donationAmount[msg.sender] += msg.value;
        emit Donated(msg.sender, msg.value);
    }

    /**
     * @dev Permite al contrato repartir tokens masivamente.
     */
    function airdropTokens(
        address tokenAddress, 
        address[] calldata recipients, 
        uint256[] calldata amounts
    ) external {
        require(recipients.length == amounts.length, "Mismatch list length");
        IERC20 token = IERC20(tokenAddress);
        for (uint256 i = 0; i < recipients.length; i++) {
            require(token.transferFrom(msg.sender, recipients[i], amounts[i]), "Transfer failed");
        }
    }

    // --- FUNCIONES PARA EL DASHBOARD ---

    function getDonors() external view returns (address[] memory) {
        return donorsList;
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }

    /**
     * @dev Solo el dueño puede retirar los fondos acumulados del contrato.
     */
    function withdrawFunds() external {
        require(msg.sender == owner, "Solo el dueno puede retirar");
        payable(owner).transfer(address(this).balance);
    }

    /**
     * @dev Distribuye ETH del balance del contrato a una lista de destinatarios.
     * Solo el owner puede llamar a esta función.
     * Es el equivalente a airdropTokens() pero repartiendo ETH en lugar de tokens.
     * Flujo: donantes envían ETH via receive() → owner redistribuye con esta función.
     */
    function airdropETH(
        address[] calldata recipients,
        uint256[] calldata amounts
    ) external {
        require(msg.sender == owner, "Solo el dueno puede distribuir");
        require(recipients.length == amounts.length, "Mismatch list length");

        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        require(address(this).balance >= total, "Saldo insuficiente en el contrato");

        for (uint256 i = 0; i < recipients.length; i++) {
            payable(recipients[i]).transfer(amounts[i]);
        }
    }
}
