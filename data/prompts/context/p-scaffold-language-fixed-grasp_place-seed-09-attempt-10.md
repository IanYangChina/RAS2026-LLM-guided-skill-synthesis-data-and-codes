## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.4949 | 0.15 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 7 | 0.4165 | 0.79 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 7 | 0.4166 | 0.79 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 7 | 0.4166 | 0.79 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 7 | 0.4164 | 0.79 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.495) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 20.0
      - 100.0
      default: 50
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: transport_arc

```

## Design Metrics

- **Composite score**: -0.495
- **task_score** (E): 0.150
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1708 |
| descend_1 | 0.00 | 1.00 | 0.0385 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.33 | 1.00 | 0.1061 |
| transport_1 | 0.67 | 1.00 | 0.1860 |
| place_descend | 0.00 | 1.00 | 0.0920 |
| release_1 | 1.00 | 1.00 | 0.0275 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.412, -0.005, 0.155) | (0.515, -0.017, 0.030)→(0.477, -0.018, 0.016) | 0.268→0.294 | 1.00 / 5.000 | 189.727 | 1365.935 |
| descend_1 | descend | 0.00 / step_budget | (0.412, -0.005, 0.155)→(0.426, -0.014, 0.178) | (0.477, -0.018, 0.016)→(0.476, -0.018, 0.016) | 0.294→0.294 | 1.00 / 5.000 | 313.988 | 464.116 |
| grasp_1 | grasp | 1.00 / step_budget | (0.426, -0.014, 0.178)→(0.426, -0.014, 0.178) | (0.476, -0.018, 0.016)→(0.476, -0.018, 0.016) | 0.294→0.294 | 1.00 / 9.667 | 182031.421 | 191.428 |
| lift_1 | lift | 0.33 / step_budget | (0.426, -0.014, 0.178)→(0.481, -0.029, 0.239) | (0.476, -0.018, 0.016)→(0.476, -0.018, 0.016) | 0.294→0.294 | 1.00 / 9.667 | 246.873 | 552.532 |
| transport_1 | approach | 0.67 / step_budget | (0.481, -0.029, 0.239)→(0.529, 0.124, 0.316) | (0.476, -0.018, 0.016)→(0.474, -0.006, 0.016) | 0.294→0.286 | 1.00 / 8.333 | 3323.669 | 262.488 |
| place_descend | descend | 0.00 / step_budget | (0.529, 0.124, 0.316)→(0.544, 0.144, 0.279) | (0.474, -0.006, 0.016)→(0.474, -0.006, 0.016) | 0.286→0.286 | 1.00 / 9.333 | 91117.811 | 467.712 |
| release_1 | release | 1.00 / step_budget | (0.544, 0.144, 0.279)→(0.544, 0.144, 0.306) | (0.474, -0.006, 0.016)→(0.474, -0.006, 0.016) | 0.286→0.286 | 1.00 / 4.000 | 0.123 | 96.427 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.172
- phase_score: 0.162
- phase_breakdown.transport_arc_score: 0.004
- phase_breakdown.descend_1_score: 0.060
- phase_breakdown.release_1_score: 0.003
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.078
- grasp_place_fitness: 0.172

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.172
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.172
- **Median Q (composite search score)**: -0.500
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30035,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06343,"descend_1.descend_speed":0.09601,"grasp_1.grasp_timeout":62.02096,"lift_1.lift_height":0.06498,"lift_1.lift_speed":0.04398,"place_descend.place_descend_speed":0.02621,"place_descend.place_z_offset":0.03598,"release_1.release_timeout":7.07809,"transport_1.hover_height":0.28815,"transport_1.transport_speed":0.08333},"optimized_scores":{"best_composite_score":-0.50002,"best_fitness_score":0.14998,"best_task_score":0.12655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64436,-0.00486,-0.00045],"force_p95":200.05832,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1455.71807,"mean_force":198.40739,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40918,-0.00476,0.13179]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.63163,-0.00941,-0.00023],"force_p95":523.37395,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":962.27624,"mean_force":280.59553,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43174,-0.01366,0.18916]},{"body_a":"world","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.58599,-0.10215,-0.00028],"force_p95":496.30651,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":529.07974,"mean_force":373.91635,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4998,-0.06647,0.27033]},{"body_a":"world","body_b":"link6","contact_count":491.0,"contact_point_centroid":[0.60217,0.20781,-0.00033],"force_p95":422.03215,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.92018,"mean_force":325.63363,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61029,0.22066,0.29331]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.67769,-0.02272,-0.00012],"force_p95":72.50442,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.10341,"mean_force":69.83346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46466,-0.02739,0.1706]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53782,0.00056,-0.00338],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.4072,"mean_force":17.06118,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38502,-0.00294,0.04729]},{"body_a":"world","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.57923,-0.09984,-9e-05],"force_p95":279.01582,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.13101,"mean_force":211.26186,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52322,-0.07833,0.28634]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.59896,0.2174,-0.00017],"force_p95":89.84992,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.26948,"mean_force":62.36816,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61139,0.22214,0.29385]},{"body_a":"link5","body_b":"hand","contact_count":639.0,"contact_point_centroid":[0.49833,-0.18244,0.23046],"force_p95":75.023,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.70655,"mean_force":55.90935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50571,-0.08081,0.27926]},{"body_a":"grasp_target","body_b":"link7","contact_count":380.0,"contact_point_centroid":[0.5225,-0.014,0.0329],"force_p95":1.14688,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.15536,"mean_force":0.43484,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39988,-0.00337,0.10368]},{"body_a":"grasp_target","body_b":"hand","contact_count":143.0,"contact_point_centroid":[0.49884,-0.0289,0.04781],"force_p95":2.22028,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99171,"mean_force":0.88741,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39453,-0.003,0.0821]},{"body_a":"world","body_b":"grasp_target","contact_count":3693.0,"contact_point_centroid":[0.50781,-0.02382,-0.00237],"force_p95":0.32921,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28932,"mean_force":0.16285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42147,-0.00454,0.14361]},{"body_a":"grasp_target","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.54544,-0.02737,0.02444],"force_p95":0.74826,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.82258,"mean_force":0.33653,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39227,-0.00301,0.08437]},{"body_a":"grasp_target","body_b":"link6","contact_count":234.0,"contact_point_centroid":[0.51931,-0.01354,0.03097],"force_p95":0.60781,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6859,"mean_force":0.37724,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53557,-0.02956,0.31137]},{"body_a":"world","body_b":"grasp_target","contact_count":3706.0,"contact_point_centroid":[0.4965,0.00802,-0.0023],"force_p95":0.34857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56711,"mean_force":0.15021,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56344,0.06437,0.3762]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5015,-0.02406,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43245,-0.01388,0.18925]}],"total_contact_groups":26},"final_pose_error":0.05041,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49595,0.01227,0.01602],"final_tcp_position":[0.61127,0.22253,0.29352],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12055,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5015,-0.02406,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33449,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":189.89379,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5246.0,"raw_peak_contact_force":1455.71807,"tcp_end":[0.42699,-0.00767,0.17314],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17466,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5015,-0.02406,0.01602],"object_pos_start":[0.5015,-0.02406,0.01602],"object_to_goal_dist_end":0.33449,"object_to_goal_dist_start":0.33449,"object_z_max":0.01602,"peak_contact_force":554.30448,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4976.0,"raw_peak_contact_force":962.27624,"tcp_end":[0.46478,-0.02732,0.17209],"tcp_start":[0.42699,-0.00767,0.17314],"tcp_to_object_dist_end":0.16036,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5015,-0.02406,0.01602],"object_pos_start":[0.5015,-0.02406,0.01602],"object_to_goal_dist_end":0.33449,"object_to_goal_dist_start":0.33449,"object_z_max":0.01602,"peak_contact_force":273004.12055,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3523.0,"raw_peak_contact_force":404.10341,"subtask_id":"grasp_1","tcp_end":[0.46465,-0.02744,0.17049],"tcp_start":[0.46465,-0.02743,0.17049],"tcp_to_object_dist_end":0.15884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5015,-0.02406,0.01602],"object_pos_start":[0.5015,-0.02406,0.01602],"object_to_goal_dist_end":0.33449,"object_to_goal_dist_start":0.33449,"object_z_max":0.01602,"peak_contact_force":402.23725,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9888.0,"raw_peak_contact_force":529.07974,"tcp_end":[0.51885,-0.08293,0.27609],"tcp_start":[0.46465,-0.02744,0.17049],"tcp_to_object_dist_end":0.26721,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.01227,0.01602],"object_pos_start":[0.5015,-0.02406,0.01602],"object_to_goal_dist_end":0.31007,"object_to_goal_dist_start":0.33449,"object_z_max":0.01727,"peak_contact_force":9749.00935,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8338.0,"raw_peak_contact_force":283.13101,"subtask_id":"transport_arc","tcp_end":[0.60185,0.19259,0.46442],"tcp_start":[0.51885,-0.08293,0.27609],"tcp_to_object_dist_end":0.49477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.01227,0.01602],"object_pos_start":[0.49595,0.01227,0.01602],"object_to_goal_dist_end":0.31007,"object_to_goal_dist_start":0.31007,"object_z_max":0.01602,"peak_contact_force":131.41408,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8794.0,"raw_peak_contact_force":503.92018,"subtask_id":"release_1","tcp_end":[0.61127,0.22253,0.29352],"tcp_start":[0.60185,0.19259,0.46442],"tcp_to_object_dist_end":0.36677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49595,0.01227,0.01602],"object_pos_start":[0.49595,0.01227,0.01602],"object_to_goal_dist_end":0.31007,"object_to_goal_dist_start":0.31007,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":90.26948,"tcp_end":[0.61162,0.22206,0.31983],"tcp_start":[0.61127,0.22253,0.29352],"tcp_to_object_dist_end":0.38691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.08019,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03803,"descend_1.descend_speed":0.02315,"grasp_1.grasp_timeout":52.95694,"lift_1.lift_height":0.09536,"lift_1.lift_speed":0.06339,"place_descend.place_descend_speed":0.03639,"place_descend.place_z_offset":0.01458,"release_1.release_timeout":4.1508,"transport_1.hover_height":0.14448,"transport_1.transport_speed":0.0454},"optimized_scores":{"best_composite_score":-0.50659,"best_fitness_score":0.14341,"best_task_score":0.15034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64404,-0.00526,-0.00045],"force_p95":197.33924,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1319.55989,"mean_force":197.08368,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40307,-0.00516,0.12253]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53714,-6e-05,-0.00311],"force_p95":360.11584,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1238.19194,"mean_force":71.23133,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38444,-0.00353,0.04811]},{"body_a":"world","body_b":"link6","contact_count":820.0,"contact_point_centroid":[0.61563,-0.01739,-0.0002],"force_p95":510.54815,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":926.14299,"mean_force":324.36853,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43146,-0.03519,0.20547]},{"body_a":"world","body_b":"link6","contact_count":945.0,"contact_point_centroid":[0.61683,0.15855,-0.00034],"force_p95":406.62147,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.42662,"mean_force":323.68656,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62677,0.15464,0.29365]},{"body_a":"world","body_b":"link5","contact_count":96.0,"contact_point_centroid":[0.52444,0.08308,-0.00019],"force_p95":381.89907,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.5044,"mean_force":261.23505,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53512,-0.02143,0.27244]},{"body_a":"world","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.56773,0.04726,-6e-05],"force_p95":247.85013,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.0095,"mean_force":105.62697,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56304,0.02673,0.29243]},{"body_a":"link5","body_b":"hand","contact_count":105.0,"contact_point_centroid":[0.51591,0.01843,0.19107],"force_p95":199.17947,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.54583,"mean_force":87.26383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46054,-0.07241,0.18891]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.62413,-0.01028,-0.00025],"force_p95":196.69202,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.99736,"mean_force":193.09647,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40128,-0.01219,0.15607]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51747,0.0734,-5e-05],"force_p95":199.41005,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.41005,"mean_force":199.41005,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54563,-0.00462,0.28189]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.62247,0.16971,-0.00016],"force_p95":88.15836,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.62085,"mean_force":61.35417,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62647,0.15661,0.29419]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61209,-0.01362,-0.00014],"force_p95":80.0629,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.0024,"mean_force":74.14566,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41433,-0.01517,0.18808]},{"body_a":"grasp_target","body_b":"link6","contact_count":153.0,"contact_point_centroid":[0.54701,-0.01646,0.02486],"force_p95":0.67489,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.76014,"mean_force":0.38063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39239,-0.00363,0.08728]},{"body_a":"grasp_target","body_b":"link7","contact_count":606.0,"contact_point_centroid":[0.53031,-0.01532,0.03287],"force_p95":1.05323,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.30448,"mean_force":0.32024,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40004,-0.0044,0.11036]},{"body_a":"world","body_b":"grasp_target","contact_count":3651.0,"contact_point_centroid":[0.51313,-0.03001,-0.00242],"force_p95":0.32601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.11192,"mean_force":0.16571,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41593,-0.00494,0.13529]},{"body_a":"grasp_target","body_b":"hand","contact_count":150.0,"contact_point_centroid":[0.49955,-0.03566,0.04733],"force_p95":2.18023,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.71336,"mean_force":0.92197,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39363,-0.00361,0.08264]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50483,-0.03069,-0.00209],"force_p95":0.15311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16657,"mean_force":0.12939,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40128,-0.01219,0.15607]}],"total_contact_groups":29},"final_pose_error":0.1029,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50426,-0.03094,0.01602],"final_tcp_position":[0.62659,0.15635,0.29385],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273002.63754,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,-0.02999,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28269,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":188.91072,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5469.0,"raw_peak_contact_force":1319.55989,"tcp_end":[0.4133,-0.00761,0.15361],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50445,-0.03086,0.01602],"object_pos_start":[0.50622,-0.02999,0.01602],"object_to_goal_dist_end":0.28409,"object_to_goal_dist_start":0.28269,"object_z_max":0.01603,"peak_contact_force":194.74407,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5527.0,"raw_peak_contact_force":220.99736,"tcp_end":[0.41403,-0.01512,0.18824],"tcp_start":[0.4133,-0.00761,0.15361],"tcp_to_object_dist_end":0.19515,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50445,-0.03086,0.01602],"object_pos_start":[0.50445,-0.03086,0.01602],"object_to_goal_dist_end":0.28409,"object_to_goal_dist_start":0.28409,"object_z_max":0.01602,"peak_contact_force":86.02143,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":82.0024,"subtask_id":"grasp_1","tcp_end":[0.41437,-0.01521,0.18799],"tcp_start":[0.41437,-0.0152,0.188],"tcp_to_object_dist_end":0.19477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50426,-0.03094,0.01602],"object_pos_start":[0.50445,-0.03086,0.01602],"object_to_goal_dist_end":0.28423,"object_to_goal_dist_start":0.28409,"object_z_max":0.01606,"peak_contact_force":228.98263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9109.0,"raw_peak_contact_force":926.14299,"tcp_end":[0.54563,-0.00462,0.28189],"tcp_start":[0.41437,-0.01521,0.18799],"tcp_to_object_dist_end":0.27035,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50426,-0.03094,0.01602],"object_pos_start":[0.50426,-0.03094,0.01602],"object_to_goal_dist_end":0.28423,"object_to_goal_dist_start":0.28423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4201.0,"raw_peak_contact_force":271.0095,"subtask_id":"transport_arc","tcp_end":[0.62534,0.15031,0.31044],"tcp_start":[0.54563,-0.00462,0.28189],"tcp_to_object_dist_end":0.36633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50426,-0.03094,0.01602],"object_pos_start":[0.50426,-0.03094,0.01602],"object_to_goal_dist_end":0.28423,"object_to_goal_dist_start":0.28423,"object_z_max":0.01602,"peak_contact_force":273002.63754,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9251.0,"raw_peak_contact_force":578.42662,"subtask_id":"release_1","tcp_end":[0.62659,0.15635,0.29385],"tcp_start":[0.62534,0.15031,0.31044],"tcp_to_object_dist_end":0.3567,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50426,-0.03094,0.01602],"object_pos_start":[0.50426,-0.03094,0.01602],"object_to_goal_dist_end":0.28423,"object_to_goal_dist_start":0.28423,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1102.0,"raw_peak_contact_force":88.62085,"tcp_end":[0.62663,0.15673,0.3203],"tcp_start":[0.62659,0.15635,0.29385],"tcp_to_object_dist_end":0.37786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.24167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06242,"descend_1.descend_speed":0.01005,"grasp_1.grasp_timeout":62.81879,"lift_1.lift_height":0.15141,"lift_1.lift_speed":0.09936,"place_descend.place_descend_speed":0.03586,"place_descend.place_z_offset":0.02297,"release_1.release_timeout":6.80354,"transport_1.hover_height":0.29911,"transport_1.transport_speed":0.09797},"optimized_scores":{"best_composite_score":-0.47798,"best_fitness_score":0.17202,"best_task_score":0.17211},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63435,-0.0001,-0.00045],"force_p95":197.12777,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1322.52716,"mean_force":198.87526,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38889,-0.0001,0.11386]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52726,0.00375,-0.003],"force_p95":358.28069,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1243.73749,"mean_force":71.38379,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37444,-0.00021,0.04796]},{"body_a":"world","body_b":"link6","contact_count":992.0,"contact_point_centroid":[0.55269,0.04289,-0.00022],"force_p95":230.18589,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.79067,"mean_force":218.75643,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.3553,0.04035,0.19031]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.58391,0.01442,-0.00024],"force_p95":230.685,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.32467,"mean_force":222.71155,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.35502,0.01364,0.14777]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61879,0.00017,-0.00025],"force_p95":193.46889,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.07418,"mean_force":192.17024,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39125,-0.00012,0.14966]},{"body_a":"world","body_b":"link6","contact_count":165.0,"contact_point_centroid":[0.60367,0.00033,-0.00025],"force_p95":202.07587,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.37231,"mean_force":195.10447,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.38382,-6e-05,0.16139]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.52596,0.05139,-0.00015],"force_p95":90.74891,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.38949,"mean_force":73.2999,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.39423,0.05198,0.24922]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.6089,0.00025,-0.00014],"force_p95":83.65461,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.17814,"mean_force":74.35109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39914,-5e-05,0.17463]},{"body_a":"grasp_target","body_b":"hand","contact_count":42.0,"contact_point_centroid":[0.44235,0.00552,0.04214],"force_p95":3.56429,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.96823,"mean_force":1.44053,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38355,-0.00019,0.05118]},{"body_a":"world","body_b":"grasp_target","contact_count":3909.0,"contact_point_centroid":[0.42706,0.00114,-0.00214],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33273,"mean_force":0.13875,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40117,-7e-05,0.12461]},{"body_a":"grasp_target","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47676,-0.00407,0.00645],"force_p95":0.25221,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2578,"mean_force":0.19375,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37289,-0.00021,0.04326]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42191,0.00134,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39125,-0.00012,0.14966]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.42191,0.00134,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39914,-5e-05,0.17463]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.42191,0.00134,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.38382,-6e-05,0.16139]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42191,0.00134,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.35504,0.01363,0.14778]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42191,0.00134,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.35549,0.04039,0.19056]}],"total_contact_groups":22},"final_pose_error":0.26015,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42191,0.00134,0.01602],"final_tcp_position":[0.39402,0.05192,0.24895],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273004.12069,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":190.37648,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4867.0,"raw_peak_contact_force":1322.52716,"tcp_end":[0.3946,-0.00011,0.13747],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12449,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":192.91622,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":209.07418,"tcp_end":[0.39879,-0.0,0.1748],"tcp_start":[0.3946,-0.00011,0.13747],"tcp_to_object_dist_end":0.16046,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":273004.12069,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":88.17814,"subtask_id":"grasp_1","tcp_end":[0.3992,-7e-05,0.17452],"tcp_start":[0.3992,-7e-05,0.17452],"tcp_to_object_dist_end":0.16012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":109.39982,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1531.0,"raw_peak_contact_force":202.37231,"tcp_end":[0.37865,3e-05,0.15932],"tcp_start":[0.3992,-7e-05,0.17452],"tcp_to_object_dist_end":0.14969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":221.87357,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9211.0,"raw_peak_contact_force":233.32467,"subtask_id":"transport_arc","tcp_end":[0.36128,0.0296,0.17438],"tcp_start":[0.37865,3e-05,0.15932],"tcp_to_object_dist_end":0.17191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":219.3816,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9212.0,"raw_peak_contact_force":320.79067,"subtask_id":"release_1","tcp_end":[0.39402,0.05192,0.24895],"tcp_start":[0.36128,0.0296,0.17438],"tcp_to_object_dist_end":0.23999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42191,0.00134,0.01602],"object_pos_start":[0.42191,0.00134,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1093.0,"raw_peak_contact_force":110.38949,"tcp_end":[0.39371,0.0519,0.27866],"tcp_start":[0.39402,0.05192,0.24895],"tcp_to_object_dist_end":0.26895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```