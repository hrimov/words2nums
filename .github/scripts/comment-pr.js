module.exports = async ({ github, context, core }) => {
  const fs = require('fs');
  const path = require('path');

  const indexHtml = fs.readFileSync('htmlcov/index.html', 'utf8');

  const totalMatch = indexHtml.match(/<span class="pc_cov">([\d.]+)%<\/span>/);
  const totalCoverage = totalMatch ? totalMatch[1] : 'N/A';

  const fileRegex = /<tr class="region">.*?<td class="name left"><a href="[^"]+">([^<]+)<\/a><\/td>.*?<td>(\d+)<\/td>.*?<td>(\d+)<\/td>.*?<td>(\d+)<\/td>.*?<td class="right"[^>]*>([\d.]+)%<\/td>.*?<\/tr>/gs;
  let filesCoverage = [];
  let match;

  while ((match = fileRegex.exec(indexHtml)) !== null) {
    const [_, file, statements, missing, excluded, coverage] = match;
    if (!file.includes('__init__')) {
      const shortFile = file.replace('src/words2nums/', '');
      filesCoverage.push(`| ${shortFile} | ${statements} | ${missing} | ${coverage}% |`);
    }
  }

  const body = `## Coverage Report
  Total coverage: ${totalCoverage}%

  ### Coverage by file
  | File | Statements | Missing | Coverage |
  |------|------------|---------|----------|
  ${filesCoverage.join('\n')}

  Full coverage report available on smokeshow - ${process.env.COVERAGE_URL}
  `;

  await github.rest.issues.createComment({
    issue_number: context.issue.number,
    owner: context.repo.owner,
    repo: context.repo.repo,
    body: body
  });
}; 