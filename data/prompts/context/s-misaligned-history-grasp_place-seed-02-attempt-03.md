## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | 0.1073 | 0.16 | ❌ rejected |
| 2 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1073 | 0.16 | ❌ rejected |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1073 | 0.16 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | -0.2015 | 0.37 | ✅ accepted |

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=-0.202) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    descend_grasp_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    descend_grasp_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    descend_grasp_z:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_goal_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_goal_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_goal_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_grasp_x: status=consumed; consumers=target.offset.x (add)
    - descend_grasp_y: status=consumed; consumers=target.offset.y (add)
    - descend_grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_x: status=consumed; consumers=target.offset.x (add)
    - approach_goal_y: status=consumed; consumers=target.offset.y (add)
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (add)
    - place_y: status=consumed; consumers=target.offset.y (add)
    - place_z: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.202
- **task_score** (E): 0.370
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1588 |
| descend_to_grasp | 1.00 | 1.00 | 0.1174 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 1.00 | 1.00 | 0.1217 |
| approach_goal | 0.00 | 1.00 | 0.1038 |
| descend_to_place | 0.33 | 1.00 | 0.1081 |
| release | 1.00 | 1.00 | 0.0214 |
| retract | 1.00 | 1.00 | 0.0852 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.013, 0.149) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.494, -0.013, 0.149)→(0.501, -0.010, 0.033) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.501, -0.010, 0.033)→(0.493, -0.010, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.011, 0.023) | 0.281→0.280 | 1.00 / 41.333 | 0.317 | 0.429 |
| lift | lift | 1.00 / step_budget | (0.493, -0.010, 0.025)→(0.489, -0.011, 0.146) | (0.493, -0.011, 0.023)→(0.498, -0.011, 0.140) | 0.280→0.237 | 1.00 / 38.000 | 0.084 | 0.808 |
| approach_goal | approach | 0.00 / step_budget | (0.489, -0.011, 0.146)→(0.546, 0.065, 0.185) | (0.498, -0.011, 0.140)→(0.557, 0.065, 0.170) | 0.237→0.139 | 1.00 / 32.667 | 0.092 | 0.125 |
| descend_to_place | descend | 0.33 / step_budget | (0.546, 0.065, 0.185)→(0.606, 0.146, 0.160) | (0.557, 0.065, 0.170)→(0.612, 0.144, 0.087) | 0.139→0.094 | 1.00 / 19.000 | 0.121 | 0.700 |
| release | release | 1.00 / step_budget | (0.606, 0.146, 0.160)→(0.600, 0.144, 0.180) | (0.612, 0.144, 0.087)→(0.615, 0.147, 0.014) | 0.094→0.155 | 1.00 / 4.000 | 0.191 | 0.913 |
| retract | retract | 1.00 / step_budget | (0.600, 0.144, 0.180)→(0.597, 0.144, 0.265) | (0.615, 0.147, 0.014)→(0.615, 0.148, 0.016) | 0.155→0.153 | 1.00 / 4.000 | 0.123 | 0.197 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.500
- phase_score: 0.375
- phase_breakdown.lift_object_score: 0.496
- phase_breakdown.reach_object_score: 0.142
- phase_breakdown.place_goal_score: 0.396
- grasp_place_fitness: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.500
- **Median Q (composite search score)**: -0.231
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88462,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00562,"approach_goal.approach_goal_y":0.0196,"approach_goal.approach_goal_z":0.09906,"approach_object.approach_offset_x":0.00575,"approach_object.approach_offset_y":0.02215,"approach_object.approach_offset_z":0.11953,"descend_to_grasp.descend_grasp_x":0.01801,"descend_to_grasp.descend_grasp_y":0.00447,"descend_to_grasp.descend_grasp_z":-0.00727,"descend_to_place.place_x":0.00612,"descend_to_place.place_y":-0.00629,"descend_to_place.place_z":-0.00494,"lift.lift_height":0.13828,"release.release_timeout":1.39477},"optimized_scores":{"best_composite_score":-0.23397,"best_fitness_score":0.64603,"best_task_score":0.30656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.60241,0.13812,-0.00709],"force_p95":1.17008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66115,"mean_force":0.41834,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60023,0.12625,0.19397]},{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.47266,-0.01122,-0.00187],"force_p95":0.55797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81327,"mean_force":0.10337,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47761,-0.01312,0.02883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15660.0,"contact_point_centroid":[0.47401,-0.03251,0.08906],"force_p95":0.0824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3841,"mean_force":0.05075,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47379,-0.01334,0.08713]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47596,-0.01898,-0.00269],"force_p95":0.29808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36396,"mean_force":0.17461,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48089,-0.01313,0.02675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15660.0,"contact_point_centroid":[0.474,0.00585,0.08898],"force_p95":0.08186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32828,"mean_force":0.0485,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47379,-0.01334,0.08713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":737.0,"contact_point_centroid":[0.60901,0.10903,0.17397],"force_p95":0.27174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32403,"mean_force":0.09366,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6039,0.1272,0.17611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.6092,0.1457,0.17453],"force_p95":0.29039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32117,"mean_force":0.10978,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60373,0.12716,0.17587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13786.0,"contact_point_centroid":[0.57524,0.07842,0.18566],"force_p95":0.10508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16858,"mean_force":0.07096,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57107,0.09692,0.18538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12583.0,"contact_point_centroid":[0.57607,0.11645,0.18546],"force_p95":0.10864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16714,"mean_force":0.07777,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57206,0.09779,0.18523]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48947,0.00085,0.23015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18466.0,"contact_point_centroid":[0.50251,0.00571,0.17459],"force_p95":0.08068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13171,"mean_force":0.05407,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5016,0.02476,0.17277]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.60434,0.13808,-0.00201],"force_p95":0.12365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12868,"mean_force":0.12048,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59744,0.12557,0.24119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4353.0,"contact_point_centroid":[0.47989,0.00618,0.02784],"force_p95":0.09631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.123,"mean_force":0.04901,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47974,-0.01312,0.02557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18548.0,"contact_point_centroid":[0.5023,0.04363,0.17447],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12266,"mean_force":0.05364,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50142,0.02456,0.17262]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48304,-0.00691,0.08451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.47997,-0.03335,0.02724],"force_p95":0.09879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10688,"mean_force":0.04735,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47977,-0.01312,0.0256]}],"total_contact_groups":16},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60434,0.13808,0.01602],"final_tcp_position":[0.59772,0.12559,0.28586],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.66115,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48019,0.00177,0.15935],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48756,-0.01316,0.0336],"tcp_start":[0.48019,0.00177,0.15935],"tcp_to_object_dist_end":0.01537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47582,-0.01369,0.02355],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28603,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.26424,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11550.0,"raw_peak_contact_force":0.36396,"tcp_end":[0.47971,-0.01311,0.02555],"tcp_start":[0.48756,-0.01316,0.0336],"tcp_to_object_dist_end":0.00442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.47906,-0.0138,0.14451],"object_pos_start":[0.47582,-0.01369,0.02355],"object_to_goal_dist_end":0.23497,"object_to_goal_dist_start":0.28603,"object_z_max":0.1444,"peak_contact_force":0.07724,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31517.0,"raw_peak_contact_force":0.81327,"subtask_id":"lift_object","tcp_end":[0.4722,-0.0136,0.15033],"tcp_start":[0.47971,-0.01311,0.02555],"tcp_to_object_dist_end":0.009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54489,0.06013,0.18274],"object_pos_start":[0.47906,-0.0138,0.14451],"object_to_goal_dist_end":0.13173,"object_to_goal_dist_start":0.23497,"object_z_max":0.18272,"peak_contact_force":0.10356,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37014.0,"raw_peak_contact_force":0.13171,"subtask_id":"place_goal","tcp_end":[0.53184,0.05992,0.19728],"tcp_start":[0.4722,-0.0136,0.15033],"tcp_to_object_dist_end":0.01954,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61283,0.12757,0.15635],"object_pos_start":[0.54489,0.06013,0.18274],"object_to_goal_dist_end":0.04979,"object_to_goal_dist_start":0.13173,"object_z_max":0.18274,"peak_contact_force":0.14886,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26369.0,"raw_peak_contact_force":0.16858,"subtask_id":"place_goal","tcp_end":[0.60584,0.12758,0.18001],"tcp_start":[0.53184,0.05992,0.19728],"tcp_to_object_dist_end":0.02467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60404,0.13557,0.01147],"object_pos_start":[0.61283,0.12757,0.15635],"object_to_goal_dist_end":0.18217,"object_to_goal_dist_start":0.04979,"object_z_max":0.15635,"peak_contact_force":0.09697,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1555.0,"raw_peak_contact_force":1.66115,"tcp_end":[0.60019,0.12625,0.20062],"tcp_start":[0.60584,0.12758,0.18001],"tcp_to_object_dist_end":0.18941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.60434,0.13808,0.01602],"object_pos_start":[0.60404,0.13557,0.01147],"object_to_goal_dist_end":0.17735,"object_to_goal_dist_start":0.18217,"object_z_max":0.01662,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12868,"tcp_end":[0.59772,0.12559,0.28586],"tcp_start":[0.60019,0.12625,0.20062],"tcp_to_object_dist_end":0.27021,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89222,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.01951,"approach_goal.approach_goal_y":-0.01493,"approach_goal.approach_goal_z":0.10321,"approach_object.approach_offset_x":-0.01081,"approach_object.approach_offset_y":0.01195,"approach_object.approach_offset_z":0.0983,"descend_to_grasp.descend_grasp_x":0.01463,"descend_to_grasp.descend_grasp_y":0.01625,"descend_to_grasp.descend_grasp_z":-0.01585,"descend_to_place.place_x":-0.00132,"descend_to_place.place_y":0.01049,"descend_to_place.place_z":-0.01768,"lift.lift_height":0.13799,"release.release_timeout":1.81248},"optimized_scores":{"best_composite_score":-0.13957,"best_fitness_score":0.74043,"best_task_score":0.50001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.58942,0.17851,-0.00531],"force_p95":0.83683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95462,"mean_force":0.33736,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58771,0.17687,0.11881]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.45492,-0.00922,-0.00265],"force_p95":0.42669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71414,"mean_force":0.13123,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45379,-0.01076,0.03122]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45855,-0.02349,-0.00331],"force_p95":0.44932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51851,"mean_force":0.22779,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45695,-0.01068,0.0276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14488.0,"contact_point_centroid":[0.45326,-0.03088,0.0899],"force_p95":0.09576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40962,"mean_force":0.05557,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4529,-0.0116,0.08826]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.61294,0.17836,-0.00204],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33976,"mean_force":0.12415,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58412,0.17571,0.17171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14314.0,"contact_point_centroid":[0.4531,0.00775,0.08904],"force_p95":0.09467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28083,"mean_force":0.05174,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45287,-0.01158,0.08689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14876.0,"contact_point_centroid":[0.56272,0.1162,0.1387],"force_p95":0.09259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17565,"mean_force":0.06511,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56078,0.13531,0.13717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2883.0,"contact_point_centroid":[0.45565,0.00954,0.03208],"force_p95":0.12513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16471,"mean_force":0.07258,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45584,-0.01068,0.02653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19026.0,"contact_point_centroid":[0.56154,0.1539,0.13754],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15978,"mean_force":0.05172,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56061,0.1351,0.13728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5345.0,"contact_point_centroid":[0.45626,-0.03434,0.02661],"force_p95":0.12487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14556,"mean_force":0.0605,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45599,-0.01068,0.02668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":934.0,"contact_point_centroid":[0.59505,0.15931,0.10851],"force_p95":0.0937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1429,"mean_force":0.05446,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59228,0.1784,0.10671]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47401,-0.00638,0.21939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1102.0,"contact_point_centroid":[0.59552,0.19727,0.10782],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13516,"mean_force":0.04749,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59237,0.17843,0.10686]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45545,-0.01171,0.07741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17906.0,"contact_point_centroid":[0.49314,0.02315,0.16345],"force_p95":0.07933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12053,"mean_force":0.05497,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4923,0.04232,0.16145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20779.0,"contact_point_centroid":[0.49157,0.05981,0.16244],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09758,"mean_force":0.04728,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49112,0.04079,0.16094]}],"total_contact_groups":16},"final_pose_error":0.01508,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61296,0.17836,0.01602],"final_tcp_position":[0.5843,0.17573,0.21638],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.95462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.44861,-0.01309,0.13812],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46331,-0.0107,0.03376],"tcp_start":[0.44861,-0.01309,0.13812],"tcp_to_object_dist_end":0.01807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45781,-0.01263,0.02136],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29508,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.39522,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10028.0,"raw_peak_contact_force":0.51851,"tcp_end":[0.45583,-0.01067,0.02651],"tcp_start":[0.46331,-0.0107,0.03376],"tcp_to_object_dist_end":0.00586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.46536,-0.01281,0.13785],"object_pos_start":[0.45781,-0.01263,0.02136],"object_to_goal_dist_end":0.2767,"object_to_goal_dist_start":0.29508,"object_z_max":0.13773,"peak_contact_force":0.09472,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29022.0,"raw_peak_contact_force":0.71414,"subtask_id":"lift_object","tcp_end":[0.45398,-0.01247,0.14813],"tcp_start":[0.45583,-0.01067,0.02651],"tcp_to_object_dist_end":0.01534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52969,0.08346,0.15656],"object_pos_start":[0.46536,-0.01281,0.13785],"object_to_goal_dist_end":0.16569,"object_to_goal_dist_start":0.2767,"object_z_max":0.15653,"peak_contact_force":0.07267,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38685.0,"raw_peak_contact_force":0.12053,"subtask_id":"place_goal","tcp_end":[0.52369,0.08348,0.17442],"tcp_start":[0.45398,-0.01247,0.14813],"tcp_to_object_dist_end":0.01885,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59725,0.17868,0.08719],"object_pos_start":[0.52969,0.08346,0.15656],"object_to_goal_dist_end":0.05176,"object_to_goal_dist_start":0.16569,"object_z_max":0.15656,"peak_contact_force":0.09253,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33902.0,"raw_peak_contact_force":0.17565,"subtask_id":"place_goal","tcp_end":[0.59437,0.17894,0.11033],"tcp_start":[0.52369,0.08348,0.17442],"tcp_to_object_dist_end":0.02333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61398,0.17808,0.01497],"object_pos_start":[0.59725,0.17868,0.08719],"object_to_goal_dist_end":0.10488,"object_to_goal_dist_start":0.05176,"object_z_max":0.08719,"peak_contact_force":0.3548,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2237.0,"raw_peak_contact_force":0.95462,"tcp_end":[0.58755,0.17682,0.13106],"tcp_start":[0.59437,0.17894,0.11033],"tcp_to_object_dist_end":0.11906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.61296,0.17836,0.01602],"object_pos_start":[0.61398,0.17808,0.01497],"object_to_goal_dist_end":0.10397,"object_to_goal_dist_start":0.10488,"object_z_max":0.01609,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.33976,"tcp_end":[0.5843,0.17573,0.21638],"tcp_start":[0.58755,0.17682,0.13106],"tcp_to_object_dist_end":0.20242,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88158,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.02468,"approach_goal.approach_goal_y":-0.00377,"approach_goal.approach_goal_z":0.08973,"approach_object.approach_offset_x":0.01787,"approach_object.approach_offset_y":-0.03161,"approach_object.approach_offset_z":0.11562,"descend_to_grasp.descend_grasp_x":0.0135,"descend_to_grasp.descend_grasp_y":-0.00438,"descend_to_grasp.descend_grasp_z":-0.00905,"descend_to_place.place_x":-0.0055,"descend_to_place.place_y":0.01932,"descend_to_place.place_z":0.01456,"lift.lift_height":0.12983,"release.release_timeout":1.40604},"optimized_scores":{"best_composite_score":-0.23106,"best_fitness_score":0.64894,"best_task_score":0.30286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.62617,0.1266,-0.00327],"force_p95":0.62336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75442,"mean_force":0.17614,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61396,0.12379,0.18786]},{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.54099,-0.00926,-0.00209],"force_p95":0.57501,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89708,"mean_force":0.1226,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54094,-0.00729,0.02503]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54426,-0.00058,-0.00284],"force_p95":0.33635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40595,"mean_force":0.18866,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54458,-0.00728,0.02321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15060.0,"contact_point_centroid":[0.53934,0.01198,0.08133],"force_p95":0.08396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39597,"mean_force":0.05127,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53913,-0.0072,0.07938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15060.0,"contact_point_centroid":[0.53937,-0.0264,0.08119],"force_p95":0.08405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32692,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53913,-0.0072,0.07938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7350.0,"contact_point_centroid":[0.59749,0.06157,0.18],"force_p95":0.15706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26556,"mean_force":0.09403,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59399,0.08043,0.18135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10401.0,"contact_point_centroid":[0.59819,0.10068,0.18095],"force_p95":0.09984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20236,"mean_force":0.06447,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59492,0.08253,0.1816]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5257,-0.01397,0.22389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3931.0,"contact_point_centroid":[0.54333,-0.02667,0.0246],"force_p95":0.10216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12991,"mean_force":0.0539,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54328,-0.00728,0.02169]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17944.0,"contact_point_centroid":[0.56154,0.0034,0.16097],"force_p95":0.08498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12299,"mean_force":0.05556,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56026,0.02241,0.1594]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.55123,-0.0156,0.07693]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6263,0.12655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6135,0.13028,0.18969]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.6263,0.12655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60935,0.1292,0.24946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5493.0,"contact_point_centroid":[0.54356,0.01341,0.02333],"force_p95":0.10374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11689,"mean_force":0.04915,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54333,-0.00727,0.02175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17344.0,"contact_point_centroid":[0.56167,0.04153,0.16124],"force_p95":0.0847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11096,"mean_force":0.05768,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56032,0.02248,0.15947]},{"body_a":"left_finger","body_b":"right_finger","contact_count":610.0,"contact_point_centroid":[0.61551,0.12601,0.19043],"force_p95":0.01343,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.0109,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61499,0.126,0.18822]}],"total_contact_groups":17},"final_pose_error":0.01527,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6263,0.12655,0.01602],"final_tcp_position":[0.60966,0.12924,0.29411],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.75442,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.55376,-0.02818,0.15014],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55196,-0.00729,0.03198],"tcp_start":[0.55376,-0.02818,0.15014],"tcp_to_object_dist_end":0.01284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54396,-0.00706,0.02298],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25746,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.29075,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11224.0,"raw_peak_contact_force":0.40595,"tcp_end":[0.54326,-0.00729,0.02167],"tcp_start":[0.55196,-0.00729,0.03198],"tcp_to_object_dist_end":0.0015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.54914,-0.00699,0.13817],"object_pos_start":[0.54396,-0.00706,0.02298],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.25746,"object_z_max":0.13805,"peak_contact_force":0.07915,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30348.0,"raw_peak_contact_force":0.89708,"subtask_id":"lift_object","tcp_end":[0.53976,-0.00709,0.13998],"tcp_start":[0.54326,-0.00729,0.02167],"tcp_to_object_dist_end":0.00956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59716,0.05056,0.17045],"object_pos_start":[0.54914,-0.00699,0.13817],"object_to_goal_dist_end":0.12056,"object_to_goal_dist_start":0.19937,"object_z_max":0.17043,"peak_contact_force":0.10081,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35288.0,"raw_peak_contact_force":0.12299,"subtask_id":"place_goal","tcp_end":[0.58342,0.05049,0.18307],"tcp_start":[0.53976,-0.00709,0.13998],"tcp_to_object_dist_end":0.01866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6263,0.12655,0.01602],"object_pos_start":[0.59716,0.05056,0.17045],"object_to_goal_dist_end":0.17917,"object_to_goal_dist_start":0.12056,"object_z_max":0.17045,"peak_contact_force":0.12262,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19180.0,"raw_peak_contact_force":1.75442,"subtask_id":"place_goal","tcp_end":[0.61743,0.13106,0.18906],"tcp_start":[0.58342,0.05049,0.18307],"tcp_to_object_dist_end":0.17332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6263,0.12655,0.01602],"object_pos_start":[0.6263,0.12655,0.01602],"object_to_goal_dist_end":0.17917,"object_to_goal_dist_start":0.17917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61198,0.12987,0.20919],"tcp_start":[0.61743,0.13106,0.18906],"tcp_to_object_dist_end":0.19373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.6263,0.12655,0.01602],"object_pos_start":[0.6263,0.12655,0.01602],"object_to_goal_dist_end":0.17917,"object_to_goal_dist_start":0.17917,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60966,0.12924,0.29411],"tcp_start":[0.61198,0.12987,0.20919],"tcp_to_object_dist_end":0.2786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```