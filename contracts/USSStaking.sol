// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./interfaces/IFarmToken.sol";

/// @title USSStaking — контракт для стейкинга USSToken с наградами в FARMToken
contract USSStaking is Ownable, ReentrancyGuard {
    IERC20 public immutable stakeToken;       // USSToken
    IFarmToken public immutable rewardToken;  // FARMToken

    uint256 public rewardRate = 1e18;         // 1 FARM per block
    uint256 public accRewardPerToken;
    uint256 public lastRewardBlock;
    uint256 public totalStaked;

    struct StakeInfo {
        uint128 amount;
        uint128 rewardDebt;
    }

    mapping(address => StakeInfo) public stakes;
    mapping(address => uint256) public pendingRewards;

    event Staked(address indexed user, uint256 amount);
    event Claimed(address indexed user, uint256 reward);
    event Withdrawn(address indexed user, uint256 amount);
    event WithdrawnAll(address indexed user, uint256 amount);

    constructor(address _stakeToken, address _rewardToken, address initialOwner)
        Ownable(initialOwner)
    {
        stakeToken = IERC20(_stakeToken);
        rewardToken = IFarmToken(_rewardToken);
        lastRewardBlock = block.number;
    }

    function updatePool() internal {
        if (block.number > lastRewardBlock && totalStaked > 0) {
            uint256 blocks = block.number - lastRewardBlock;
            uint256 reward = blocks * rewardRate;
            accRewardPerToken += (reward * 1e18) / totalStaked;
        }
        lastRewardBlock = block.number;
    }

    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Amount must be > 0");
        StakeInfo storage user = stakes[msg.sender];
        updatePool();

        if (user.amount > 0) {
            uint256 pending = (uint256(user.amount) * accRewardPerToken) / 1e18 - user.rewardDebt;
            if (pending > 0) {
                pendingRewards[msg.sender] += pending;
            }
        }

        stakeToken.transferFrom(msg.sender, address(this), amount);
        user.amount += uint128(amount);
        user.rewardDebt = uint128((uint256(user.amount) * accRewardPerToken) / 1e18);
        totalStaked += amount;

        emit Staked(msg.sender, amount);
    }

    function claim() external nonReentrant {
        updatePool();
        StakeInfo storage user = stakes[msg.sender];
        uint256 pending = (uint256(user.amount) * accRewardPerToken) / 1e18 - user.rewardDebt + pendingRewards[msg.sender];
        require(pending > 0, "No rewards");

        user.rewardDebt = uint128((uint256(user.amount) * accRewardPerToken) / 1e18);
        pendingRewards[msg.sender] = 0;
        rewardToken.mint(msg.sender, pending);

        emit Claimed(msg.sender, pending);
    }

    function withdraw(uint256 amount) external nonReentrant {
        StakeInfo storage user = stakes[msg.sender];
        require(user.amount >= amount, "Insufficient amount");
        updatePool();

        uint256 pending = (uint256(user.amount) * accRewardPerToken) / 1e18 - user.rewardDebt + pendingRewards[msg.sender];
        pendingRewards[msg.sender] = 0;

        user.amount -= uint128(amount);
        user.rewardDebt = uint128((uint256(user.amount) * accRewardPerToken) / 1e18);
        totalStaked -= amount;

        stakeToken.transfer(msg.sender, amount);
        if (pending > 0) rewardToken.mint(msg.sender, pending);

        emit Withdrawn(msg.sender, amount);
    }

    function withdrawAll() external nonReentrant {
        StakeInfo storage user = stakes[msg.sender];
        uint256 amount = user.amount;
        require(amount > 0, "Nothing to withdraw");
        updatePool();

        uint256 pending = (uint256(user.amount) * accRewardPerToken) / 1e18 - user.rewardDebt + pendingRewards[msg.sender];
        pendingRewards[msg.sender] = 0;

        user.amount = 0;
        user.rewardDebt = 0;
        totalStaked -= amount;

        stakeToken.transfer(msg.sender, amount);
        if (pending > 0) rewardToken.mint(msg.sender, pending);

        emit WithdrawnAll(msg.sender, amount);
    }

    function setRewardRate(uint256 newRate) external onlyOwner {
        updatePool();
        rewardRate = newRate;
    }

    function emergencyWithdrawTokens(address token, address to, uint256 amount) external onlyOwner {
        IERC20(token).transfer(to, amount);
    }

    // 🔧 Для фронтенда
    function stakedBalance(address user) public view returns (uint256) {
        return stakes[user].amount;
    }

    function calculateReward(address user) public view returns (uint256) {
        StakeInfo storage info = stakes[user];

        uint256 currentAccRewardPerToken = accRewardPerToken;
        if (block.number > lastRewardBlock && totalStaked > 0) {
            uint256 blocks = block.number - lastRewardBlock;
            uint256 reward = blocks * rewardRate;
            currentAccRewardPerToken += (reward * 1e18) / totalStaked;
        }

        uint256 pending = ((uint256(info.amount) * currentAccRewardPerToken) / 1e18)
                          - info.rewardDebt + pendingRewards[user];

        return pending;
    }
}

