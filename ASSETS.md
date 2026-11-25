<div align="center">
  <img width="1024" height="256" alt="PyStSlides" src="./assets/banner.svg" />
</div>

<br>

-----

<div align="center">
  <strong>Catálogo visual dos 30 assets editoriais incluídos no pacote PyStSlides (<code>PNG</code> e <code>SVG</code>).</strong>
</div>

<br>

<p align="center">
  <a href="./README.md">README</a> •
  <a href="./TUTORIAL.md">Tutorial</a> •
  <a href="./examples/README.md">Exemplos</a>
</p>

-----

<br>

## **Como Usar os Assets**

Você pode usar as ilustrações diretamente do pacote instalado ou exportá-las para uma pasta local:

```python
from pystslides import Presentation, get_editorial_assets_dir

with Presentation(title="Minha Apresentação", assets_dir=get_editorial_assets_dir()) as deck:
    deck.cover(title="Título", image="discovery_cover.png", image_position="right")
    deck.split_slide("Arquitetura", "Fluxo distribuído.", media="api_gateway.svg")
```

```bash
# Ou copie todos os 30 assets para ./assets
pystslides-assets ./assets
```

<br>

## **Catálogo Visual (Grade 10 × 3)**

<table>
  <tbody>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/access_desk.png" width="240" alt="access_desk.png" /><br>
        <code>access_desk.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/access_governance.svg" width="240" alt="access_governance.svg" /><br>
        <code>access_governance.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/ai_pipeline.png" width="240" alt="ai_pipeline.png" /><br>
        <code>ai_pipeline.png</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/ai_shield.svg" width="240" alt="ai_shield.svg" /><br>
        <code>ai_shield.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/api_gateway.svg" width="240" alt="api_gateway.svg" /><br>
        <code>api_gateway.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/classification_network.png" width="240" alt="classification_network.png" /><br>
        <code>classification_network.png</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/classification_nodes.svg" width="240" alt="classification_nodes.svg" /><br>
        <code>classification_nodes.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/cloud_architecture.png" width="240" alt="cloud_architecture.png" /><br>
        <code>cloud_architecture.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/cloud_nodes.svg" width="240" alt="cloud_nodes.svg" /><br>
        <code>cloud_nodes.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/code_review.svg" width="240" alt="code_review.svg" /><br>
        <code>code_review.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/coverage_laptop.png" width="240" alt="coverage_laptop.png" /><br>
        <code>coverage_laptop.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/coverage_workspace.svg" width="240" alt="coverage_workspace.svg" /><br>
        <code>coverage_workspace.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/database_cluster.svg" width="240" alt="database_cluster.svg" /><br>
        <code>database_cluster.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/discovery_analytics.svg" width="240" alt="discovery_analytics.svg" /><br>
        <code>discovery_analytics.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/discovery_cover.png" width="240" alt="discovery_cover.png" /><br>
        <code>discovery_cover.png</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/event_bus.svg" width="240" alt="event_bus.svg" /><br>
        <code>event_bus.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/interactive_quiz.svg" width="240" alt="interactive_quiz.svg" /><br>
        <code>interactive_quiz.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/lock_verification.svg" width="240" alt="lock_verification.svg" /><br>
        <code>lock_verification.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/metrics_dashboard.svg" width="240" alt="metrics_dashboard.svg" /><br>
        <code>metrics_dashboard.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/ml_training.svg" width="240" alt="ml_training.svg" /><br>
        <code>ml_training.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/observability_traces.svg" width="240" alt="observability_traces.svg" /><br>
        <code>observability_traces.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/performance_growth.png" width="240" alt="performance_growth.png" /><br>
        <code>performance_growth.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/remediation_analytics.png" width="240" alt="remediation_analytics.png" /><br>
        <code>remediation_analytics.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/remediation_automation.svg" width="240" alt="remediation_automation.svg" /><br>
        <code>remediation_automation.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/roadmap_planning.png" width="240" alt="roadmap_planning.png" /><br>
        <code>roadmap_planning.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/security_audit.png" width="240" alt="security_audit.png" /><br>
        <code>security_audit.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/stepper_journey.svg" width="240" alt="stepper_journey.svg" /><br>
        <code>stepper_journey.svg</code>
      </td>
    </tr>
    <tr>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/team_collaboration.png" width="240" alt="team_collaboration.png" /><br>
        <code>team_collaboration.png</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/timeline_milestones.svg" width="240" alt="timeline_milestones.svg" /><br>
        <code>timeline_milestones.svg</code>
      </td>
      <td align="center" width="33%">
        <img src="./src/pystslides/editorial_assets/workflow_sync.svg" width="240" alt="workflow_sync.svg" /><br>
        <code>workflow_sync.svg</code>
      </td>
    </tr>
  </tbody>
</table>
