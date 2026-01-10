module.exports = {
  platform: 'github',
  
  // This makes sure the bot knows how to setup new repos
  onboardingConfig: {
    extends: ['config:recommended'], 
  },

  // Your repository list
  repositories: ['belly-rewardz/mastering-devops-sre'],
  
  // Optional: If you want to customize the author
  gitAuthor: "Renovate Bot <bot@renovateapp.com>",
};