## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4863 | 0.50 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3469 | 0.65 | ✅ accepted |
| 0 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.4974 | 0.27 | ✅ accepted |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.486) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.1
  weight: 0.3
- id: push_to_goal
  weight: 0.7
phases:
- id: approach_lateral
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.04
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.15
    - 0.3
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_lateral** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.04, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.04, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.15, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.486
- **task_score** (E): 0.500
- **fitness_score**: 0.716  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.2619 |
| push_to_goal | 1.00 | 1.00 | 0.1986 |
| retract | 0.00 | 1.00 | 0.1624 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.038, 0.047) | (0.513, 0.002, 0.025)→(0.514, 0.002, 0.025) | 0.160→0.160 | 1.00 / 2.667 | 50.797 | 134.480 |
| push_to_goal | push | 1.00 / step_budget | (0.512, 0.038, 0.047)→(0.496, -0.152, 0.023) | (0.514, 0.002, 0.025)→(0.535, -0.083, 0.026) | 0.160→0.080 | 1.00 / 3.000 | 0.370 | 116.006 |
| retract | retract | 0.00 / step_budget | (0.496, -0.152, 0.023)→(0.496, -0.150, 0.185) | (0.535, -0.083, 0.026)→(0.536, -0.083, 0.025) | 0.080→0.080 | 1.00 / 4.000 | 0.245 | 0.844 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.581
- lateral_force_integral: None
- approach_alignment: 0.863
- goal_progress: 0.544
- terminal_score: 0.544
- phase_score: 0.905
- phase_breakdown.push_to_goal_score: 0.989
- phase_breakdown.reach_pre_contact_score: 0.709

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.761
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.544
- **Median Q (composite search score)**: 0.465
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.243


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93056,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.03526,"approach_side.approach_z_offset":0.01666,"push_to_goal.push_extension":0.02034,"push_to_goal.push_speed":0.07099},"optimized_scores":{"best_composite_score":0.53051,"best_fitness_score":0.76051,"best_task_score":0.54374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":508.0,"contact_point_centroid":[0.47886,-0.04724,0.04719],"force_p95":183.63775,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.05679,"mean_force":151.67659,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47715,-0.05409,0.04619]},{"body_a":"world","body_b":"push_box","contact_count":985.0,"contact_point_centroid":[0.48079,-0.05632,-0.00073],"force_p95":166.87639,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.19713,"mean_force":78.97657,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47615,-0.05396,0.04546]},{"body_a":"world","body_b":"push_box","contact_count":3938.0,"contact_point_centroid":[0.49468,-0.09152,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04299,"mean_force":0.25069,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49697,-0.14934,0.10577]},{"body_a":"world","body_b":"push_box","contact_count":3128.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.47409,0.00168,0.17521]}],"total_contact_groups":4},"final_pose_error":0.11372,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49467,-0.09164,0.02499],"final_tcp_position":[0.49727,-0.14933,0.18631],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":192.05679,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.44952,0.0034,0.05144],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.49317,-0.09378,0.02711],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05667,"object_to_goal_dist_start":0.12843,"object_z_max":0.0366,"peak_contact_force":0.62064,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1493.0,"raw_peak_contact_force":192.05679,"subtask_id":"push_to_goal","tcp_end":[0.50044,-0.15021,0.02474],"tcp_start":[0.44952,0.0034,0.05144],"tcp_to_object_dist_end":0.05694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49467,-0.09164,0.02499],"object_pos_start":[0.49317,-0.09378,0.02711],"object_to_goal_dist_end":0.0586,"object_to_goal_dist_start":0.05667,"object_z_max":0.02711,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3938.0,"raw_peak_contact_force":2.04299,"tcp_end":[0.49727,-0.14933,0.18631],"tcp_start":[0.50044,-0.15021,0.02474],"tcp_to_object_dist_end":0.17135,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40476,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.03621,"approach_side.approach_z_offset":0.00848,"push_to_goal.push_extension":0.02281,"push_to_goal.push_speed":0.03804},"optimized_scores":{"best_composite_score":0.46475,"best_fitness_score":0.69475,"best_task_score":0.4655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.55607,0.02725,0.04781],"force_p95":197.93379,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":239.35463,"mean_force":137.31428,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.54866,0.03579,0.04799]},{"body_a":"world","body_b":"push_box","contact_count":3525.0,"contact_point_centroid":[0.55347,0.00175,-2e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":213.44669,"mean_force":2.44885,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.5225,0.01772,0.1691]},{"body_a":"attachment","body_b":"push_box","contact_count":167.0,"contact_point_centroid":[0.5396,-0.0336,0.04922],"force_p95":36.16915,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.90125,"mean_force":9.83677,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53124,-0.02373,0.03333]},{"body_a":"world","body_b":"push_box","contact_count":1093.0,"contact_point_centroid":[0.55995,-0.07882,-0.0001],"force_p95":13.09066,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.6876,"mean_force":1.88639,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51379,-0.08356,0.02783]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55964,-0.08839,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49244,-0.15068,0.10178]}],"total_contact_groups":5},"final_pose_error":0.11578,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55964,-0.08839,0.02499],"final_tcp_position":[0.49468,-0.15008,0.18434],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":239.35463,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.55348,-0.00083,0.02526],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.15847,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":1.25232,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3581.0,"raw_peak_contact_force":239.35463,"subtask_id":"reach_pre_contact","tcp_end":[0.55236,0.03756,0.04336],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.55964,-0.08839,0.02499],"object_pos_start":[0.55348,-0.00083,0.02526],"object_to_goal_dist_end":0.08575,"object_to_goal_dist_start":0.15847,"object_z_max":0.02808,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1260.0,"raw_peak_contact_force":68.90125,"subtask_id":"push_to_goal","tcp_end":[0.49384,-0.15213,0.02156],"tcp_start":[0.55236,0.03756,0.04336],"tcp_to_object_dist_end":0.09167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55964,-0.08839,0.02499],"object_pos_start":[0.55964,-0.08839,0.02499],"object_to_goal_dist_end":0.08575,"object_to_goal_dist_start":0.08575,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49468,-0.15008,0.18434],"tcp_start":[0.49384,-0.15213,0.02156],"tcp_to_object_dist_end":0.18281,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41148,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.03913,"approach_side.approach_z_offset":0.01297,"push_to_goal.push_extension":0.02376,"push_to_goal.push_speed":0.0444},"optimized_scores":{"best_composite_score":0.46364,"best_fitness_score":0.69364,"best_task_score":0.49092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.5397,0.06282,0.04838],"force_p95":150.66756,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.84125,"mean_force":126.28285,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.53201,0.0717,0.04902]},{"body_a":"world","body_b":"push_box","contact_count":3520.0,"contact_point_centroid":[0.53671,0.03729,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.04528,"mean_force":1.43854,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.51448,0.03566,0.17195]},{"body_a":"attachment","body_b":"push_box","contact_count":201.0,"contact_point_centroid":[0.52858,-0.00778,0.04929],"force_p95":37.08395,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.06036,"mean_force":9.24376,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5198,0.00104,0.03656]},{"body_a":"world","body_b":"push_box","contact_count":1206.0,"contact_point_centroid":[0.55274,-0.05731,-9e-05],"force_p95":13.74165,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.01748,"mean_force":1.95228,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50736,-0.07442,0.02922]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55225,-0.0683,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49287,-0.15186,0.10199]}],"total_contact_groups":5},"final_pose_error":0.11556,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55225,-0.0683,0.02499],"final_tcp_position":[0.49492,-0.15075,0.18456],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":163.84125,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.53811,0.03801,0.02476],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":150.89487,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3553.0,"raw_peak_contact_force":163.84125,"subtask_id":"reach_pre_contact","tcp_end":[0.53443,0.07348,0.04727],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.55225,-0.0683,0.02499],"object_pos_start":[0.53811,0.03801,0.02476],"object_to_goal_dist_end":0.09698,"object_to_goal_dist_start":0.19183,"object_z_max":0.02831,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1407.0,"raw_peak_contact_force":87.06036,"subtask_id":"push_to_goal","tcp_end":[0.49447,-0.15384,0.02167],"tcp_start":[0.53443,0.07348,0.04727],"tcp_to_object_dist_end":0.10328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55225,-0.0683,0.02499],"object_pos_start":[0.55225,-0.0683,0.02499],"object_to_goal_dist_end":0.09698,"object_to_goal_dist_start":0.09698,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49492,-0.15075,0.18456],"tcp_start":[0.49447,-0.15384,0.02167],"tcp_to_object_dist_end":0.18854,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```