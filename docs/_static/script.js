document.addEventListener('load', () => {
  try {
    document.querySelector('.edit-this-page').remove()
    
    // remove these useless crap that appears on official readthedocs builds
    document.querySelector('#furo-readthedocs-versions').remove()
    document.querySelector('.injected').remove()
  } catch {
    // we're building this locally, forget it
  }
})

const findChildrenWithName = (elem, name) => [...elem.children].find(child => child.nodeName === name)

for (const label of document.querySelectorAll('.sidebar-container label')) {
  const link = findChildrenWithName(label.parentElement, 'A')

  link.addEventListener('click', event => {
    event.preventDefault()
    label.click()
  })
}