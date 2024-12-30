module.exports = async ({ github, context, core }) => {
  const fs = require('fs');
  const xml = fs.readFileSync('coverage.xml', 'utf8');
  const match = xml.match(/line-rate="([\d.]+)"/);
  const coverage = match ? Math.round(parseFloat(match[1]) * 100) : 0;
  
  await github.rest.repos.createCommitStatus({
    owner: context.repo.owner,
    repo: context.repo.repo,
    sha: context.sha,
    state: 'success',
    description: `coverage ${coverage}%`,
    context: 'coverage',
    target_url: process.env.COVERAGE_URL
  });
};
