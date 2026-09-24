## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | time_limit | 4 | 0.1448 | 0.37 | ❌ rejected |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | time_limit | 4 | 0.6262 | 0.86 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.8165 | 0.97 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.8120 | 0.99 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | 0.0920 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- Frozen realised-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`
- Frozen initial hinge angle: 0.106 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.1065
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.992, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.145) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_handle
  weight: 0.3
- id: push_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_handle
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.04
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_door
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.04, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.145
- **task_score** (E): 0.375
- **fitness_score**: 0.375  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach | 1.00 | 0.1596 |
| push | 1.00 | 0.1285 |
| retract | 1.00 | 0.0880 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.240, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| push | push | 1.00 / time_limit | (0.100, 0.240, 0.348)→(0.024, 0.136, 0.356) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| retract | retract | 1.00 / time_limit | (0.024, 0.136, 0.356)→(0.022, 0.136, 0.444) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.477
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.477
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.477
- **Median Q (composite search score)**: 0.142
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.202


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":10.0,"average_failure_rate":0.0885,"average_mean_iterations":22.77876,"average_solve_count":113.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08253,"push.push_distance":0.25059,"push.push_max_time":1234.87284,"push.push_speed":0.09987},"optimized_scores":{"best_composite_score":0.14192,"best_fitness_score":0.37192,"best_task_score":0.37192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link7","contact_count":396.0,"contact_point_centroid":[0.01218,0.10895,0.37126],"force_p95":819.11762,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":918.64854,"mean_force":418.65543,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.01382,0.134,0.35695]},{"body_a":"door_panel","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.10266,0.15609,0.48503],"force_p95":645.28549,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":664.79555,"mean_force":604.01597,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.02141,0.13045,0.35283]},{"body_a":"link2","body_b":"link5","contact_count":72.0,"contact_point_centroid":[-0.08271,0.09643,0.3242],"force_p95":158.04468,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.89149,"mean_force":63.32281,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.02042,0.27867,0.39882]},{"body_a":"door_panel","body_b":"link5","contact_count":507.0,"contact_point_centroid":[0.1099,0.11447,0.54239],"force_p95":230.68437,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.52189,"mean_force":165.66102,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.01894,0.12809,0.39898]},{"body_a":"door_panel","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.10331,0.14896,0.48818],"force_p95":92.98763,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.93027,"mean_force":34.60754,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02169,0.12966,0.35633]},{"body_a":"link1","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.02392,0.10776,0.37126],"force_p95":113.35535,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.2601,"mean_force":105.48083,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02197,0.12988,0.35254]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.30217,0.16898,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09976,0.3193,0.34822]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30209,0.16951,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.00151,0.20378,0.38865]},{"body_a":"world","body_b":"door_panel","contact_count":560.0,"contact_point_centroid":[0.30682,0.14834,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.019,0.12805,0.39706]}],"total_contact_groups":9},"final_pose_error":0.01477,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.02008,0.13248,0.43801],"hinge_angle":0.30135,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.09995,0.23962,0.34828],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43441,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_door","tcp_end":[0.02204,0.12986,0.35242],"tcp_start":[0.09995,0.23962,0.34828],"tcp_to_object_dist_end":0.37623,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.02008,0.13248,0.43801],"tcp_start":[0.02204,0.12986,0.35242],"tcp_to_object_dist_end":0.45805,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.09184,"average_mean_iterations":24.08163,"average_solve_count":98.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.1199,"push.push_distance":0.21622,"push.push_max_time":1506.55645,"push.push_speed":0.09985},"optimized_scores":{"best_composite_score":0.24744,"best_fitness_score":0.47744,"best_task_score":0.47744},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":72.0,"contact_point_centroid":[-0.08367,0.09266,0.32509],"force_p95":167.67912,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1346.13611,"mean_force":93.53741,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.01687,0.27466,0.40106]},{"body_a":"link1","body_b":"link7","contact_count":393.0,"contact_point_centroid":[0.01278,0.11129,0.37021],"force_p95":709.23026,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":890.77284,"mean_force":410.61359,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.02331,0.14413,0.35584]},{"body_a":"door_panel","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.10154,0.16728,0.4744],"force_p95":584.21789,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":587.13812,"mean_force":527.65424,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.02962,0.14201,0.35021]},{"body_a":"door_panel","body_b":"link5","contact_count":296.0,"contact_point_centroid":[0.10869,0.11837,0.5544],"force_p95":184.27867,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.53679,"mean_force":127.90272,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02768,0.1404,0.4115]},{"body_a":"door_panel","body_b":"link6","contact_count":126.0,"contact_point_centroid":[0.10304,0.15125,0.49927],"force_p95":72.84822,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.62183,"mean_force":46.83292,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02924,0.14136,0.36703]},{"body_a":"link1","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.01636,0.11495,0.3618],"force_p95":120.29134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.6929,"mean_force":82.08312,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.03,0.14191,0.34903]},{"body_a":"door_panel","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.15205,0.18924,0.39422],"force_p95":31.71309,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.14932,"mean_force":16.46393,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09994,0.24621,0.34823]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.15087,0.18054,0.39449],"force_p95":37.97433,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.05479,"mean_force":36.32649,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.09992,0.23789,0.34721]},{"body_a":"world","body_b":"door_panel","contact_count":316.0,"contact_point_centroid":[0.30016,0.1872,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09979,0.31637,0.34823]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30131,0.17508,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.00689,0.19991,0.38671]},{"body_a":"world","body_b":"door_panel","contact_count":620.0,"contact_point_centroid":[0.30488,0.156,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.0283,0.14078,0.39356]}],"total_contact_groups":11},"final_pose_error":0.01131,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.02711,0.14024,0.43809],"hinge_angle":0.2635,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":345.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.09995,0.23958,0.34826],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43437,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_door","tcp_end":[0.03005,0.14185,0.3489],"tcp_start":[0.09995,0.23958,0.34826],"tcp_to_object_dist_end":0.37783,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.02711,0.14024,0.43809],"tcp_start":[0.03005,0.14185,0.3489],"tcp_to_object_dist_end":0.46079,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.14563,"average_mean_iterations":34.62136,"average_solve_count":103.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.12535,"push.push_distance":0.19723,"push.push_max_time":1331.87485,"push.push_speed":0.06113},"optimized_scores":{"best_composite_score":0.04492,"best_fitness_score":0.27492,"best_task_score":0.27492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.01198,0.10798,0.37195],"force_p95":853.72511,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":955.26064,"mean_force":439.37701,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.02921,0.13254,0.37353]},{"body_a":"link2","body_b":"link5","contact_count":109.0,"contact_point_centroid":[-0.07487,0.10105,0.31875],"force_p95":160.33411,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.10482,"mean_force":72.80917,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.03106,0.28233,0.39176]},{"body_a":"link1","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.00686,0.10972,0.3729],"force_p95":187.22295,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.02058,"mean_force":87.58929,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02103,0.13728,0.36694]},{"body_a":"door_panel","body_b":"link6","contact_count":269.0,"contact_point_centroid":[0.10362,0.14822,0.56384],"force_p95":173.36126,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":226.9073,"mean_force":127.27728,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.01996,0.13565,0.43048]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.15094,0.18122,0.39453],"force_p95":41.25969,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.41522,"mean_force":38.74087,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.10007,0.23799,0.34723]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.15159,0.18421,0.39481],"force_p95":17.26761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27744,"mean_force":17.04553,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.1,0.24117,0.34831]},{"body_a":"world","body_b":"door_panel","contact_count":296.0,"contact_point_centroid":[0.30062,0.18134,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09976,0.32385,0.34818]},{"body_a":"world","body_b":"door_panel","contact_count":996.0,"contact_point_centroid":[0.30144,0.17408,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[-0.02172,0.23447,0.39709]},{"body_a":"world","body_b":"door_panel","contact_count":592.0,"contact_point_centroid":[0.30227,0.16907,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.02042,0.13628,0.40906]}],"total_contact_groups":9},"final_pose_error":0.01102,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.01965,0.13575,0.45609],"hinge_angle":0.18772,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":342.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.1,0.23988,0.34832],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43459,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_door","tcp_end":[0.02114,0.1372,0.36691],"tcp_start":[0.1,0.23988,0.34832],"tcp_to_object_dist_end":0.39229,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":574.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.01965,0.13575,0.45609],"tcp_start":[0.02114,0.1372,0.36691],"tcp_to_object_dist_end":0.47627,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```